# FastroAI Architecture Discussion

This document captures the architectural direction for FastroAI's orchestration layer.

## Core Philosophy

FastroAI started as a wrapper around PydanticAI to add production concerns:
- **Cost tracking** with microcent precision (avoids floating-point billing errors)
- **Usage visibility** (tokens, processing time) on every call
- **Safe tools** with timeout, retry, and graceful error handling
- **Tracing** via a protocol-based interface for any observability backend

The goal is to extend these "goodies" from a single agent call up through the full orchestration hierarchy: **agent → step → pipeline**.

---

## The Hierarchy

```
Pipeline
  ├── config: PipelineConfig (defaults for everything below)
  ├── tracer: Tracer (passed down)
  ├── usage: PipelineUsage (aggregated from steps)
  │
  └── Step
        ├── config: StepConfig (inherits from pipeline, can override)
        ├── context: StepContext (receives tracer, deps, tracks usage)
        ├── usage: StepUsage (aggregated from agents)
        │
        └── Agent
              ├── config: inherited/overridden (timeout, retries)
              ├── tracer: inherited from step
              └── usage: ChatResponse (single call)
```

---

## What Bubbles Up

| Level | Produces | Contains |
|-------|----------|----------|
| **Agent call** | `ChatResponse` | cost_microcents, tokens, processing_time_ms, tool_calls, trace_span |
| **Step** | `StepUsage` | sum(agent costs), sum(tokens), step_time_ms, agent_calls[], step_span |
| **Pipeline** | `PipelineUsage` | sum(step costs), sum(tokens), pipeline_time_ms, by_step{}, pipeline_span |

Each level aggregates data from the level below, providing full visibility at any point.

---

## Configuration Inheritance

**Principle**: Lower level inherits from higher, can override.

### Configuration Classes

```python
@dataclass
class ExecutionConfig:
    timeout: float | None = None        # None = no timeout
    retries: int = 0                    # 0 = no retries
    retry_delay: float = 1.0            # Base delay for exponential backoff
    cost_budget: int | None = None      # Max microcents, None = unlimited
    on_error: Literal["fail", "continue"] = "fail"

@dataclass
class PipelineConfig(ExecutionConfig):
    trace: bool = True                  # Create pipeline-level span
    # defaults apply to all steps unless overridden

@dataclass
class StepConfig(ExecutionConfig):
    trace: bool = True                  # Create step-level span
    # defaults apply to all agent calls unless overridden
```

### Resolution Example

```python
pipeline_config = PipelineConfig(timeout=120, retries=0)
step_config = StepConfig(timeout=30, retries=3)  # overrides pipeline
agent_call_config = {"timeout": 10}              # overrides step

# Agent call gets: timeout=10, retries=3 (inherited from step)
```

---

## The API

### Pipeline Level

```python
pipeline = Pipeline(
    name="research",
    steps={"classify": ClassifyStep(), "write": WriteStep()},
    dependencies={"write": ["classify"]},
    config=PipelineConfig(
        timeout=120.0,
        retries=0,
        cost_budget=500_000,  # $5 max
        trace=True,
    ),
    step_configs={
        "classify": StepConfig(timeout=10.0, retries=2),
        "write": StepConfig(timeout=60.0, cost_budget=400_000),
    },
)

result = await pipeline.execute(
    inputs={"topic": "AI"},
    deps=my_deps,
    tracer=SimpleTracer(),  # or auto-created if trace=True
)

# Result has full visibility
result.output                           # Final output
result.usage.total_cost_microcents     # 125000
result.usage.total_cost_dollars        # 1.25
result.usage.total_tokens              # 15000
result.usage.processing_time_ms        # 3500
result.usage.by_step["classify"]       # StepUsage
result.usage.by_step["write"]          # StepUsage
```

### Step Level

```python
class WriteStep(BaseStep[MyDeps, Report]):
    writer = FastroAgent(model="gpt-4o", system_prompt="...")
    reviewer = FastroAgent(model="gpt-4o-mini", system_prompt="...")

    async def execute(self, ctx: StepContext[MyDeps]) -> Report:
        # ctx.run() handles: tracer passing, usage capture, config inheritance
        draft = await ctx.run(self.writer, "Write about X")

        # Can override config per-call
        review = await ctx.run(self.reviewer, f"Review: {draft.content}",
                               timeout=5.0, retries=1)

        return Report(content=draft.content, review=review.content)
```

After execution, `ctx.usage` contains:
- `cost_microcents`: sum of writer + reviewer
- `tokens`: sum of all calls
- `agent_calls`: list of individual call records
- `processing_time_ms`: step total

### StepContext Interface

```python
class StepContext(Generic[DepsT]):
    # Passed in
    deps: DepsT
    tracer: Tracer
    config: StepConfig  # Merged from pipeline + step-specific

    # Built during execution
    usage: StepUsage

    async def run(
        self,
        agent: FastroAgent[OutputT],
        message: str,
        # Per-call overrides (override step config)
        timeout: float | None = None,
        retries: int | None = None,
    ) -> ChatResponse[OutputT]:
        """Run agent with automatic config inheritance and usage tracking."""

        effective_timeout = timeout if timeout is not None else self.config.timeout
        effective_retries = retries if retries is not None else self.config.retries

        # Execute with inherited tracer, timeout wrapper, retry logic
        response = await self._execute_with_config(
            agent, message, effective_timeout, effective_retries
        )

        # Capture usage
        self.usage.record(response)

        return response
```

---

## Full Example

```python
# Define agents (reusable)
classifier = FastroAgent(
    model="gpt-4o-mini",
    system_prompt="Classify topics into categories.",
    output_type=Classification,
)

writer = FastroAgent(
    model="gpt-4o",
    system_prompt="Write detailed reports.",
)

# Define steps
class ClassifyStep(BaseStep[MyDeps, Classification]):
    async def execute(self, ctx: StepContext[MyDeps]) -> Classification:
        topic = ctx.get_input("topic")
        response = await ctx.run(classifier, f"Classify: {topic}")
        return response.output  # Classification object

class WriteStep(BaseStep[MyDeps, str]):
    async def execute(self, ctx: StepContext[MyDeps]) -> str:
        classification = ctx.get_dependency("classify", Classification)
        response = await ctx.run(writer, f"Write about {classification.category}")
        return response.content

# Define pipeline
pipeline = Pipeline(
    name="research",
    steps={"classify": ClassifyStep(), "write": WriteStep()},
    dependencies={"write": ["classify"]},
    config=PipelineConfig(timeout=60.0, cost_budget=100_000),
    step_configs={
        "classify": StepConfig(timeout=5.0, retries=2),
    },
)

# Execute
result = await pipeline.execute({"topic": "quantum computing"}, deps=None)

print(f"Output: {result.output}")
print(f"Total cost: ${result.usage.total_cost_dollars:.4f}")
print(f"Classify cost: ${result.usage.by_step['classify'].cost_dollars:.4f}")
print(f"Write cost: ${result.usage.by_step['write'].cost_dollars:.4f}")
```

---

## Trace Hierarchy

When tracing is enabled, spans are automatically nested:

```
pipeline.research [3500ms, $1.25]
  ├── step.classify [500ms, $0.05]
  │     └── agent.gpt-4o-mini [450ms, $0.05]
  └── step.write [3000ms, $1.20]
        └── agent.gpt-4o [2900ms, $1.20]
```

---

## Key Design Decisions

### 1. `ctx.run()` as the Integration Point

The `StepContext.run()` method is where all the magic happens:
- Passes tracer to agent automatically
- Captures usage from response
- Applies timeout/retry config with inheritance
- Records agent call metadata

This is explicit (you see where agent calls happen) but not verbose.

### 2. Configuration Inheritance, Not Duplication

Instead of repeating config at every level, lower levels inherit from higher:
- Pipeline sets defaults
- Steps override what they need
- Individual calls override further

### 3. Usage Bubbles Up Automatically

No manual aggregation needed:
- Agent call → response with usage
- Step context records each call → step usage
- Pipeline executor collects step usages → pipeline usage

### 4. Agents as Class Attributes (Optional Pattern)

Defining agents as class attributes on steps:
```python
class MyStep(BaseStep):
    classifier = FastroAgent(...)
```

This is a convention, not a requirement. Agents can also be:
- Module-level constants
- Created inline in execute()
- Injected via deps

---

## Open Questions

1. **Cost budget enforcement**: Should we fail immediately when budget exceeded, or complete current call and fail before next?

2. **Retry scope**: Should step-level retries retry the whole step, or just individual agent calls?

3. **Error aggregation**: When `on_error="continue"`, how do we surface partial failures in the result?

4. **Streaming**: How does `ctx.run_stream()` work with usage tracking? (Usage only available at end of stream)

---

## Current vs Proposed

| Feature | Current Implementation | Proposed |
|---------|----------------------|----------|
| Usage tracking | Per-agent only | Agent → Step → Pipeline |
| Config inheritance | None | Pipeline → Step → Agent call |
| Tracer passing | Manual | Automatic via ctx.run() |
| Timeout/retry | @safe_tool only | All levels |
| Cost budgets | None | All levels |

---
---
---

# Part 2: API Design & Progressive Disclosure

This section explores how FastroAI's API should be designed, drawing inspiration from FastAPI's progressive disclosure and maintaining consistency with PydanticAI.

---

## FastAPI's Progressive Disclosure (Inspiration)

```python
# Level 1: Hello world (5 lines)
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello"}

# Level 2: Add path params, types validate automatically
@app.get("/items/{item_id}")
def get_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# Level 3: Dependencies when you need them
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Level 4: Middleware, events, advanced config
app = FastAPI(on_startup=[...], middleware=[...])
```

**What makes it work:**
- Simplest case is truly simple
- Types drive behavior (no config needed)
- Features are additive (you opt-in to complexity)
- Sensible defaults everywhere

---

## PydanticAI's Patterns (Consistency Target)

```python
# Core: Agent + run
agent = Agent('openai:gpt-4o', system_prompt='...')
result = await agent.run('Hello')
print(result.output)

# Structured output via type
agent = Agent('openai:gpt-4o', output_type=MyModel)

# Tools via decorator
@agent.tool
def search(ctx: RunContext[MyDeps], query: str) -> str:
    return ctx.deps.search(query)

# Deps passed at runtime
result = await agent.run('Search for X', deps=MyDeps(...))

# Streaming
async with agent.run_stream('Hello') as stream:
    async for text in stream.stream_text():
        print(text)
```

**Patterns to preserve:**
- `Agent(model, system_prompt, output_type)` constructor
- `agent.run(prompt, deps=, message_history=)` signature
- `@agent.tool` decorator pattern
- `result.output` for the response

---

## FastroAI Progressive Disclosure

### Level 1: Single Agent (mirrors PydanticAI + adds cost)

```python
from fastroai import FastroAgent

agent = FastroAgent("openai:gpt-4o")
response = await agent.run("Hello!")

print(response.content)
print(f"Cost: ${response.cost_dollars:.4f}")
```

**What you get for free:** cost tracking, token counts, timing.

---

### Level 2: System Prompt + Structured Output

```python
from pydantic import BaseModel

class Analysis(BaseModel):
    sentiment: str
    confidence: float

agent = FastroAgent(
    "openai:gpt-4o",
    system_prompt="Analyze sentiment.",
    output_type=Analysis,
)

response = await agent.run("I love this product!")
print(response.output.sentiment)  # "positive" - typed!
print(response.output.confidence) # 0.95
```

---

### Level 3: Tools (two paths)

**Path A: Use PydanticAI directly (escape hatch)**
```python
from pydantic_ai import Agent

pydantic_agent = Agent('openai:gpt-4o')

@pydantic_agent.tool
def search(query: str) -> str:
    return external_api.search(query)

# Wrap with FastroAgent for cost tracking
agent = FastroAgent(agent=pydantic_agent)
response = await agent.run("Search for AI news")
```

**Path B: Use safe_tool for production**
```python
from fastroai import FastroAgent, SafeToolset, safe_tool

@safe_tool(timeout=10.0, retries=2)
async def search(query: str) -> str:
    return await external_api.search(query)

agent = FastroAgent(
    "openai:gpt-4o",
    toolsets=[SafeToolset([search])],
)
```

---

### Level 4: Tracing

```python
from fastroai import FastroAgent, SimpleTracer

tracer = SimpleTracer()  # or your OpenTelemetry tracer
response = await agent.run("Hello", tracer=tracer)

# Logs: span timing, tokens, cost
```

---

### Level 5: Simple Pipeline

```python
from fastroai import Pipeline, BaseStep, StepContext

class AnalyzeStep(BaseStep[None, Analysis]):
    agent = FastroAgent("openai:gpt-4o", output_type=Analysis)

    async def execute(self, ctx: StepContext[None]) -> Analysis:
        text = ctx.get_input("text")
        response = await ctx.run(self.agent, f"Analyze: {text}")
        return response.output

pipeline = Pipeline(
    name="analyzer",
    steps={"analyze": AnalyzeStep()},
)

result = await pipeline.execute({"text": "Great product!"}, deps=None)
print(result.output)  # Analysis object
print(f"Cost: ${result.usage.total_cost_dollars:.4f}")
```

---

### Level 6: Multi-Step Pipeline with Dependencies

```python
class ExtractStep(BaseStep[None, list[str]]):
    async def execute(self, ctx: StepContext[None]) -> list[str]:
        response = await ctx.run(extractor, ctx.get_input("text"))
        return response.output

class SummarizeStep(BaseStep[None, str]):
    async def execute(self, ctx: StepContext[None]) -> str:
        topics = ctx.get_dependency("extract", list[str])
        response = await ctx.run(summarizer, f"Summarize: {topics}")
        return response.content

pipeline = Pipeline(
    name="extract-and-summarize",
    steps={
        "extract": ExtractStep(),
        "summarize": SummarizeStep(),
    },
    dependencies={"summarize": ["extract"]},
)
```

---

### Level 7: Full Configuration

```python
from fastroai import Pipeline, PipelineConfig, StepConfig

pipeline = Pipeline(
    name="research",
    steps={...},
    dependencies={...},
    config=PipelineConfig(
        timeout=120.0,
        cost_budget=500_000,  # $5 max
        trace=True,
    ),
    step_configs={
        "extract": StepConfig(timeout=10.0, retries=3),
        "summarize": StepConfig(timeout=60.0),
    },
)

result = await pipeline.execute(
    inputs={"text": "..."},
    deps=MyDeps(db=db, user=user),
    tracer=my_tracer,
)

# Full visibility
print(result.usage.by_step["extract"].cost_dollars)
print(result.usage.by_step["summarize"].cost_dollars)
print(result.usage.total_cost_dollars)
```

---

## API Consistency Matrix

| Concept | PydanticAI | FastroAI | Notes |
|---------|------------|----------|-------|
| Create agent | `Agent(model, ...)` | `FastroAgent(model, ...)` | Same pattern |
| Run | `agent.run(prompt)` | `agent.run(message)` | Same |
| Stream | `agent.run_stream()` | `agent.run_stream()` | Same |
| Output | `result.output` | `response.output` | Same |
| Deps | `deps=MyDeps()` | `deps=MyDeps()` | Same |
| History | `message_history=` | `message_history=` | Same |
| Tools | `@agent.tool` | escape hatch or `SafeToolset` | Compatible |
| **Cost** | - | `response.cost_dollars` | FastroAI adds |
| **Tracing** | - | `tracer=` parameter | FastroAI adds |
| **Pipelines** | - | `Pipeline`, `BaseStep` | FastroAI adds |

---

## Key Design Principles

1. **Level 1 must be trivial** - Single agent with cost tracking in 4 lines
2. **PydanticAI compatible** - Same constructor args, same run() signature
3. **Escape hatch always available** - `FastroAgent(agent=pydantic_agent)`
4. **Features are additive** - Tracing, pipelines, config are opt-in
5. **Types drive behavior** - `output_type=` gives you typed output
6. **ctx.run() is the integration point** - Where step-level features happen

---
---
---

# Part 3: Current State vs Planned State Analysis

This section provides a detailed gap analysis between what's currently implemented and what's planned.

---

## 1. FastroAgent

| Aspect | Current (Implemented) | Planned (Architecture Doc) | Gap |
|--------|----------------------|---------------------------|-----|
| Constructor | `FastroAgent(model, system_prompt, output_type, toolsets, agent=)` | Same | None |
| Run | `agent.run(message, deps, message_history, tracer)` | Same | None |
| Stream | `agent.run_stream(...)` | Same | None |
| Response | `ChatResponse[OutputT]` with cost_microcents, tokens, timing | Same | None |
| `as_step()` | `agent.as_step(prompt)` → `AgentStepWrapper` | Not mentioned in arch doc | **Exists but not discussed** |

**Current `as_step()` implementation (already exists):**

```python
# From agent.py
def as_step(
    self,
    prompt: Callable[[StepContext[DepsT]], str] | str,
) -> AgentStepWrapper[DepsT, OutputT]:
    """Turn this agent into a pipeline step."""
    return AgentStepWrapper(self, prompt)


class AgentStepWrapper(BaseStep[DepsT, OutputT]):
    async def execute(self, context: StepContext[DepsT]) -> OutputT:
        message = self._prompt if isinstance(self._prompt, str) else self._prompt(context)
        response = await self._agent.run(
            message=message,
            deps=context.deps,
            tracer=context.tracer,
        )
        self._last_usage = StepUsage.from_chat_response(response)
        return response.output
```

---

## 2. StepContext

| Aspect | Current (Implemented) | Planned (Architecture Doc) | Gap |
|--------|----------------------|---------------------------|-----|
| `get_input(key)` | Yes | Same | None |
| `get_dependency(step_id)` | Yes | Same | None |
| `deps` property | Yes | Same | None |
| `tracer` property | Yes | Same | None |
| `config` property | **No** | `StepConfig` with timeout, retries | **Missing** |
| `usage` property | **No** | `StepUsage` aggregator | **Missing** |
| `run(agent, message)` | **No** | Auto tracer, usage tracking, config | **Missing - KEY** |

**Current StepContext (no `run()` method):**

```python
class StepContext(Generic[DepsT]):
    def __init__(self, step_id, inputs, deps, step_outputs, tracer=None):
        self._step_id = step_id
        self._inputs = inputs
        self._deps = deps
        self._outputs = step_outputs
        self._tracer = tracer

    # Has: get_input, get_dependency, deps, tracer
    # Missing: config, usage, run()
```

---

## 3. Pipeline

| Aspect | Current (Implemented) | Planned (Architecture Doc) | Gap |
|--------|----------------------|---------------------------|-----|
| Constructor | `Pipeline(name, steps, dependencies, output_step)` | + `config`, `step_configs` | **Missing config params** |
| Execute | `pipeline.execute(inputs, deps, tracer)` | Same | None |
| Result | `PipelineResult` with output, step_outputs, usage | Same | Partial |
| Usage tracking | Extracts from `step.last_usage` or output | `ctx.usage` aggregation | **Different approach** |
| Config inheritance | **No** | Pipeline → Step → Agent | **Missing** |

**Current Pipeline usage extraction approach:**

```python
# From executor.py - relies on convention, not enforcement
def _extract_usage(self, step: BaseStep, output: Any) -> StepUsage | None:
    # Checks step.last_usage property
    if hasattr(step, "last_usage"):
        usage = getattr(step, "last_usage", None)
        if isinstance(usage, StepUsage):
            return usage

    # Or checks output.usage
    if hasattr(output, "usage") and isinstance(output.usage, StepUsage):
        return output.usage

    # Or converts ChatResponse
    if isinstance(output, ChatResponse):
        return StepUsage.from_chat_response(output)
```

---

## 4. BaseStep

| Aspect | Current (Implemented) | Planned (Architecture Doc) | Gap |
|--------|----------------------|---------------------------|-----|
| Abstract class | `BaseStep[DepsT, OutputT]` | Same | None |
| Execute method | `execute(context) -> OutputT` | Same | None |
| Usage tracking | Via `last_usage` property (convention) | Via `ctx.usage` | **Different approach** |

---

## 5. Configuration Classes

| Aspect | Current (Implemented) | Planned (Architecture Doc) | Gap |
|--------|----------------------|---------------------------|-----|
| `AgentConfig` | Yes (model, system_prompt, temp, etc.) | Same | None |
| `ExecutionConfig` | **No** | timeout, retries, cost_budget, on_error | **Missing** |
| `PipelineConfig` | **No** | Extends ExecutionConfig + trace | **Missing** |
| `StepConfig` | **No** | Extends ExecutionConfig + trace | **Missing** |
| Inheritance | **No** | Pipeline → Step → Agent call | **Missing** |

---

## 6. Tools

| Aspect | Current (Implemented) | Planned (Architecture Doc) | Gap |
|--------|----------------------|---------------------------|-----|
| `@safe_tool` | Yes (timeout, retries, graceful errors) | Same | None |
| `SafeToolset` | Yes | Same | None |
| `FunctionToolsetBase` | Yes | Same | None |

**Tools are complete - no changes needed.**

---

## 7. Tracing

| Aspect | Current (Implemented) | Planned (Architecture Doc) | Gap |
|--------|----------------------|---------------------------|-----|
| `Tracer` protocol | Yes | Same | None |
| `SimpleTracer` | Yes | Same | None |
| `NoOpTracer` | Yes | Same | None |
| Auto-passing to agents | **Manual only** | Via `ctx.run()` | **Part of ctx.run()** |

**Tracing infrastructure is complete. Auto-passing depends on `ctx.run()`.**

---

## Summary: What Works vs What's Missing

### Already Working Well

1. **FastroAgent** - Complete, mirrors PydanticAI, adds cost tracking
2. **`agent.as_step(prompt)`** - Handles single-agent steps with automatic usage tracking
3. **Pipeline DAG execution** - Parallel execution, dependencies, early termination
4. **Usage schemas** - `StepUsage`, `PipelineUsage` with aggregation and `__add__`
5. **`@safe_tool`** - Production-ready tool decorator
6. **Tracing infrastructure** - Protocol-based, pluggable

### Gaps to Fill

| Gap | Impact | Complexity |
|-----|--------|-----------|
| **`ctx.run(agent, msg)`** | Enables multi-agent steps with auto-tracking | Medium |
| **`ctx.usage`** | Aggregates usage within a step | Low |
| **`ctx.config`** | Provides inherited config to step | Low |
| **`PipelineConfig`/`StepConfig`** | Configuration hierarchy | Low |
| **Config inheritance logic** | Pipeline → Step → Agent call | Medium |

---

## Pattern Clarification: `as_step()` vs `ctx.run()`

The architecture doc shows `ctx.run()` in examples, but the codebase also has `agent.as_step()`. These are **complementary patterns** for different use cases:

### Pattern A: `as_step()` - Single Agent, Prompt-Focused (EXISTS)

```python
# For simple single-agent steps where you just build a prompt
agent = FastroAgent(model="gpt-4o", output_type=Summary)
step = agent.as_step(lambda ctx: f"Summarize: {ctx.get_input('text')}")

pipeline = Pipeline(
    name="summarizer",
    steps={"summarize": step},
)
```

**When to use**: Single agent, no conditional logic, just prompt building.

### Pattern B: `ctx.run()` - Multi-Agent, Logic-Focused (PLANNED)

```python
# For complex steps with multiple agents or conditional logic
class ResearchStep(BaseStep[MyDeps, Report]):
    classifier = FastroAgent(model="gpt-4o-mini", output_type=Category)
    writer = FastroAgent(model="gpt-4o")

    async def execute(self, ctx: StepContext[MyDeps]) -> Report:
        category = await ctx.run(self.classifier, "Classify this topic")

        if category.needs_research:
            # Conditional logic
            research = await ctx.run(self.researcher, "Research...")
            content = await ctx.run(self.writer, f"Write about {research}")
        else:
            content = await ctx.run(self.writer, "Write brief summary")

        return Report(category=category, content=content)
```

**When to use**: Multiple agents, conditional logic, complex orchestration.

---

## Key Observation

The architecture doc's examples use `ctx.run()`:

```python
response = await ctx.run(self.agent, f"Analyze: {text}")
```

But **`ctx.run()` doesn't exist yet**. The document describes the target state, not current state.

**Current workaround** requires manual tracer passing and no automatic usage aggregation:

```python
# What you have to do TODAY for multi-agent steps
class MyStep(BaseStep[MyDeps, str]):
    agent1 = FastroAgent(...)
    agent2 = FastroAgent(...)

    async def execute(self, ctx: StepContext[MyDeps]) -> str:
        # Manual tracer passing
        r1 = await self.agent1.run("msg1", deps=ctx.deps, tracer=ctx.tracer)
        r2 = await self.agent2.run("msg2", deps=ctx.deps, tracer=ctx.tracer)

        # No automatic usage aggregation - would need to manually track
        # self._last_usage = r1.usage + r2.usage  # Not even possible cleanly

        return f"{r1.content} {r2.content}"
```

---

## Implementation Priority

Based on this analysis:

1. **High Priority**: `ctx.run()` - This is the key missing piece that enables the planned architecture
2. **Medium Priority**: `StepConfig`, `PipelineConfig` - Enables configuration inheritance
3. **Low Priority**: Function decorators for steps - `as_step()` already covers simple cases

---
---
---

# Part 4: Refined API Design

This section consolidates the final API design decisions.

---

## Core Principles

1. **Steps can have complex logic** - conditionals, loops, multiple agent calls, external APIs
2. **Pipeline needs explicit DAG** - separate dependencies dict, not magic inference
3. **Progressive disclosure** - simple things simple, complex things possible
4. **Configuration at all levels** - step, pipeline defaults, pipeline overrides

---

## Three Step Patterns

All three patterns are equivalent under the hood and work interchangeably in pipelines.

### Pattern 1: `agent.as_step()` - Simplest

For single-agent steps where you just build a prompt.

```python
from fastroai import FastroAgent, StepConfig

classifier = FastroAgent("gpt-4o-mini", output_type=Category)

# Static prompt
classify = classifier.as_step("Classify this text")

# Dynamic prompt
classify = classifier.as_step(
    prompt=lambda ctx: f"Classify: {ctx.get_input('text')}",
    config=StepConfig(timeout=30),
)
```

**When to use**: Single agent, no conditional logic, just prompt building.

### Pattern 2: `@step` Decorator - Concise

For any logic, less boilerplate than classes.

```python
from fastroai import step

@step
def preprocess(ctx):
    """Simple transform - no agent."""
    return ctx.get_input("text").strip().lower()

@step(timeout=30, retries=2)
async def research(ctx):
    """Complex logic with multiple agents."""
    category = await ctx.run(classifier, f"Classify: {ctx.get_input('text')}")

    if category.confidence < 0.8:
        # Conditional logic
        category = await ctx.run(classifier, f"Classify with more context: ...")

    if category.type == "technical":
        sources = await ctx.run(searcher, f"Find sources for {category.name}")
        return await ctx.run(technical_writer, f"Write using {sources}")

    return await ctx.run(simple_writer, f"Write about {category.name}")

@step
def format_output(ctx):
    """Access outputs from previous steps."""
    research_result = ctx.get_dependency("research")
    return f"## Report\n\n{research_result}"
```

**When to use**: Any complexity, prefer concise syntax.

### Pattern 3: Class-Based - Explicit

For full control and clear structure.

```python
from fastroai import BaseStep, StepContext, StepConfig

class ResearchStep(BaseStep[MyDeps, Report]):
    """Explicit class with typed generics."""

    config = StepConfig(timeout=30, retries=2)

    # Agents as class attributes
    classifier = FastroAgent("gpt-4o-mini", output_type=Category)
    writer = FastroAgent("gpt-4o")

    async def execute(self, ctx: StepContext[MyDeps]) -> Report:
        category = await ctx.run(self.classifier, f"Classify: {ctx.get_input('text')}")

        if category.type == "technical":
            content = await ctx.run(self.writer, f"Technical write: {category}")
        else:
            content = await ctx.run(self.writer, f"Simple write: {category}")

        return Report(category=category, content=content)
```

**When to use**: Need explicit types, complex initialization, or prefer OOP style.

---

## Pipeline Definition

Pipeline uses a **separate dependencies dict** for explicit DAG structure:

```python
from fastroai import Pipeline, PipelineConfig, StepConfig

pipeline = Pipeline(
    name="research",
    steps={
        "preprocess": preprocess,
        "research": research,
        "analyze": analyze,
        "summarize": summarize,
        "combine": combine,
        "format": format_output,
    },
    dependencies={
        "research": ["preprocess"],
        "analyze": ["research"],
        "summarize": ["research"],      # analyze & summarize run in PARALLEL
        "combine": ["analyze", "summarize"],
        "format": ["combine"],
    },
)
```

**Parallelism is explicit**: Steps with the same dependencies run in parallel.

```
preprocess
    │
    ▼
 research
    │
    ├──────────┐
    ▼          ▼
 analyze   summarize   ← PARALLEL
    │          │
    └────┬─────┘
         ▼
      combine
         │
         ▼
       format
```

---

## Configuration Hierarchy

Three levels of configuration, with clear override order:

```python
pipeline = Pipeline(
    name="research",
    steps={
        "preprocess": preprocess,                    # No config
        "research": research,                        # Has @step(timeout=30)
        "analyze": AnalyzeStep(),                    # Has class config
        "format": format_output,
    },
    dependencies={...},

    # Level 1: Pipeline defaults (lowest priority)
    config=PipelineConfig(
        timeout=120,
        retries=0,
        cost_budget=500_000,
    ),

    # Level 3: Per-step overrides (highest priority)
    step_configs={
        "research": StepConfig(timeout=60),  # Overrides the 30 from @step
    },
)
```

**Resolution order** (highest to lowest):

1. `step_configs["step_id"]` - Pipeline-specific override
2. Step's own config - From `@step(...)` or `class.config`
3. `PipelineConfig` - Pipeline-wide defaults

---

## Configuration Classes

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class StepConfig:
    timeout: float | None = None
    retries: int = 0
    retry_delay: float = 1.0
    cost_budget: int | None = None  # In microcents

@dataclass
class PipelineConfig(StepConfig):
    """Pipeline config with additional options."""
    trace: bool = True
    on_error: Literal["fail", "continue"] = "fail"
```

---

## Full Example

```python
from fastroai import (
    FastroAgent,
    Pipeline,
    PipelineConfig,
    StepConfig,
    BaseStep,
    StepContext,
    step,
)

# --- Agents (reusable) ---
classifier = FastroAgent("gpt-4o-mini", output_type=Category)
writer = FastroAgent("gpt-4o")
reviewer = FastroAgent("gpt-4o-mini")

# --- Steps ---

# Pattern 1: as_step for simple single-agent
classify = classifier.as_step(
    lambda ctx: f"Classify: {ctx.get_input('text')}"
)

# Pattern 2: @step decorator for concise complex logic
@step
def preprocess(ctx):
    return ctx.get_input("text").strip().lower()

@step(timeout=60, retries=2)
async def write_report(ctx):
    category = ctx.get_dependency("classify", Category)

    draft = await ctx.run(writer, f"Write about {category.name}")

    if ctx.get_input("review_required", False):
        review = await ctx.run(reviewer, f"Review: {draft.content}")
        if "needs revision" in review.content.lower():
            draft = await ctx.run(writer, f"Revise based on: {review.content}")

    return draft.content

# Pattern 3: Class for explicit structure
class FormatStep(BaseStep[None, str]):
    config = StepConfig(timeout=5)

    async def execute(self, ctx: StepContext[None]) -> str:
        report = ctx.get_dependency("write_report", str)
        title = ctx.get_input("title", "Report")
        return f"# {title}\n\n{report}"

# --- Pipeline ---
pipeline = Pipeline(
    name="research",
    steps={
        "preprocess": preprocess,
        "classify": classify,
        "write_report": write_report,
        "format": FormatStep(),
    },
    dependencies={
        "classify": ["preprocess"],
        "write_report": ["classify"],
        "format": ["write_report"],
    },
    config=PipelineConfig(
        timeout=120,
        cost_budget=1_000_000,  # $10 max
    ),
)

# --- Execute ---
result = await pipeline.execute(
    inputs={"text": "Quantum computing basics", "title": "Quantum Report"},
    deps=None,
)

print(result.output)
print(f"Total cost: ${result.usage.total_cost_dollars:.4f}")
print(f"Steps: {list(result.usage.steps.keys())}")
```

---

## Progressive Disclosure Summary

| Level | What You Need | Pattern |
|-------|---------------|---------|
| 1 | Single agent call with cost tracking | `FastroAgent.run()` |
| 2 | Single agent as pipeline step | `agent.as_step(prompt)` |
| 3 | Step with logic (concise) | `@step` decorator |
| 4 | Step with logic (explicit) | `class XStep(BaseStep)` |
| 5 | Multi-step pipeline | `Pipeline(steps=..., dependencies=...)` |
| 6 | Full config control | `PipelineConfig`, `StepConfig`, `step_configs` |

---

## Key Design Decisions

1. **`@step` decorator creates class-equivalent** - Same capabilities, less boilerplate
2. **Dependencies are explicit** - Separate dict, no magic inference, clear parallelism
3. **Config cascades down** - Pipeline → Step → Override
4. **`ctx.run()` is the integration point** - Handles tracer, usage, config inheritance
5. **Three patterns coexist** - `as_step()`, `@step`, `class` all work in same pipeline

---
---
---

# Part 5: Error Hierarchy & Design Rationale

---

## Error Hierarchy

Clear exception types for different failure modes:

```python
class FastroAIError(Exception):
    """Base exception for all FastroAI errors."""
    pass


class PipelineValidationError(FastroAIError):
    """Invalid pipeline configuration.

    Raised at pipeline construction time for:
    - Unknown step in dependencies
    - Circular dependencies
    - Multiple terminal steps without explicit output_step
    """
    pass


class StepExecutionError(FastroAIError):
    """A pipeline step failed during execution.

    Attributes:
        step_id: Which step failed
        original_error: The underlying exception
    """

    def __init__(self, step_id: str, original_error: Exception):
        self.step_id = step_id
        self.original_error = original_error
        super().__init__(f"Step '{step_id}' failed: {original_error}")


class CostBudgetExceeded(FastroAIError):
    """Cost budget was exceeded.

    Attributes:
        budget_microcents: The configured budget
        actual_microcents: What was spent
        step_id: Where it was exceeded (if in pipeline)
    """

    def __init__(self, budget: int, actual: int, step_id: str | None = None):
        self.budget_microcents = budget
        self.actual_microcents = actual
        self.step_id = step_id
        location = f" in step '{step_id}'" if step_id else ""
        super().__init__(
            f"Cost budget exceeded{location}: "
            f"{actual} microcents > {budget} microcents budget"
        )
```

### Usage Pattern

```python
from fastroai import Pipeline, StepExecutionError, PipelineValidationError

# Validation errors at construction
try:
    pipeline = Pipeline(
        name="bad",
        steps={"a": step_a},
        dependencies={"a": ["nonexistent"]},  # Invalid!
    )
except PipelineValidationError as e:
    print(f"Config error: {e}")

# Execution errors at runtime
try:
    result = await pipeline.execute(inputs, deps)
except StepExecutionError as e:
    print(f"Step '{e.step_id}' failed: {e.original_error}")

    # Handle specific step failures
    if e.step_id == "fetch_external":
        return fallback_response()
    raise
```

### Error Categories

| Exception | When | Contains |
|-----------|------|----------|
| `PipelineValidationError` | Construction time | Config issue description |
| `StepExecutionError` | Execution time | `step_id`, `original_error` |
| `CostBudgetExceeded` | Execution time | `budget`, `actual`, `step_id` |

---

## Design Rationale

Why these specific design choices:

| Choice | Why |
|--------|-----|
| **Microcents (integers)** | Floating-point precision errors compound in billing. `0.1 + 0.2 = 0.30000000000000004` is unacceptable for money. |
| **Tracer protocol** | Apps integrate their own observability (Logfire, OpenTelemetry, Datadog). We provide the interface, not the implementation. |
| **No memory persistence** | Storage is app domain. Redis? PostgreSQL? DynamoDB? Your choice. We return data, you persist it. |
| **Generic `DepsT`** | Apps define their own dependency types. Your DB session, user context, API clients - all type-safe. |
| **`ctx.run()` integration point** | Single place where tracer passing, usage tracking, and config inheritance happen. Explicit but not verbose. |
| **ConversationState** | Clear signal for multi-turn pause/resume. Pipeline knows when to stop early vs continue. |
| **`@safe_tool` decorator** | Tools shouldn't crash conversations. Timeout + retry + graceful error messages keep the AI responsive. |
| **Topological levels** | Enable automatic parallelism. Steps at same level with no inter-dependencies run concurrently. |
| **Separate dependencies dict** | Explicit DAG structure. No magic inference of data flow. You see exactly what runs in parallel. |
| **Three step patterns** | Progressive disclosure. `as_step()` for simple, `@step` for concise, `class` for explicit. All equivalent. |

---

## What FastroAI is NOT

Clear boundaries:

- ❌ **Not a database ORM** - Use SQLAlchemy, Tortoise, etc.
- ❌ **Not a web framework** - Use FastAPI, Starlette, etc.
- ❌ **Not a billing system** - We calculate costs, you charge customers
- ❌ **Not a memory/RAG system** - We pass `message_history`, you load/store it
- ❌ **Not a competitor to PydanticAI** - We're built ON PydanticAI, adding orchestration

FastroAI is **orchestration primitives**. Your app provides everything else.

---

## Already Implemented: BasePipeline Router

**Note**: This is ALREADY IMPLEMENTED in `fastroai/pipelines/router.py`.

For complex routing scenarios, the router pattern selects between pipelines:

```python
class InvestmentRouter(BasePipeline[MyDeps, dict, Plan]):
    def __init__(self):
        super().__init__("investment_router")
        self.register_pipeline("simple", simple_pipeline)
        self.register_pipeline("complex", complex_pipeline)

    async def route(self, input_data, deps) -> str:
        if input_data.get("amount", 0) < 10000:
            return "simple"
        return "complex"

router = InvestmentRouter()
result = await router.execute({"amount": 50000}, deps)
```

Use cases:
- **Simple vs complex paths** - Route based on input complexity
- **A/B testing** - Split traffic between pipeline variants
- **Fallback pipelines** - Try primary, fall back to secondary

---
---
---

# Implementation Journal

This section captures implementation ideas, potential improvements, and decisions made during development.

---

## Consider: `genai-prices` Package for Model Pricing

**Date:** 2025-12-16

**Context:** Currently, FastroAI maintains its own `DEFAULT_PRICING` dict in `usage/calculator.py` with hardcoded microcents-per-1K-tokens values for each model. This requires manual updates when providers change prices or add new models.

**Proposal:** Use the `genai-prices` package from Pydantic team (https://github.com/pydantic/genai-prices) instead of maintaining our own pricing data.

**Benefits:**
- Auto-updating prices via `UpdatePrices` background downloader
- Covers more providers and models than our current list
- Maintained by Pydantic team - good fit since we build on PydanticAI
- Extracts usage from raw response data with `extract_usage()`
- Small footprint (~26KB compressed data)

**Key Features:**
```python
from genai_prices import Usage, calc_price, extract_usage, UpdatePrices

# Calculate price directly
price = calc_price(
    Usage(input_tokens=1000, output_tokens=100),
    model_ref='gpt-4o',
    provider_id='openai',
)
print(f"${price.total_price}")

# Or extract from response data
response_data = {'model': 'gpt-4o', 'usage': {'prompt_tokens': 100, 'completion_tokens': 200}}
extracted = extract_usage(response_data, provider_id='openai', api_flavor='chat')
print(extracted.calc_price().total_price)

# Auto-update prices in background
with UpdatePrices() as updater:
    updater.wait()  # Wait for initial download
    price = calc_price(...)
```

**Considerations:**
1. **Custom pricing override** - Users with volume discounts need to pass custom prices. Design API to accept override dict that takes precedence over genai-prices.
2. **Microcents conversion** - genai-prices returns floats in dollars. Need to convert: `int(price.total_price * 1_000_000)`.
3. **Offline support** - If UpdatePrices can't download, should fall back gracefully. May want to bundle a snapshot of prices.
4. **Optional dependency** - Could make genai-prices optional, fall back to our DEFAULT_PRICING if not installed.

**Proposed API:**
```python
class CostCalculator:
    def __init__(
        self,
        pricing_overrides: dict[str, dict[str, int]] | None = None,
        use_genai_prices: bool = True,  # Use genai-prices if available
    ):
        self.overrides = pricing_overrides or {}
        self._use_genai_prices = use_genai_prices and _genai_prices_available()

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> int:
        # Check overrides first (custom pricing takes precedence)
        if model in self.overrides:
            return self._calculate_from_override(model, input_tokens, output_tokens)

        # Use genai-prices if available
        if self._use_genai_prices:
            return self._calculate_from_genai_prices(model, input_tokens, output_tokens)

        # Fall back to bundled DEFAULT_PRICING
        return self._calculate_from_default(model, input_tokens, output_tokens)
```

**Status:** ✅ Implemented (2025-12-16)

**Implementation Notes:**
- Added `genai-prices>=0.7.0` as dependency
- `CostCalculator` now uses `genai_prices.calc_price()` for all pricing lookups
- Removed `DEFAULT_PRICING` dict - genai-prices provides comprehensive model coverage
- Custom pricing via `pricing_overrides` parameter (dict with `input_per_mtok`, `output_per_mtok`)
- `add_pricing_override(model, input_per_mtok, output_per_mtok)` for runtime overrides
- genai-prices returns `Decimal` - converted to int microcents for our API
- Unknown models return 0 cost (graceful degradation)

---
