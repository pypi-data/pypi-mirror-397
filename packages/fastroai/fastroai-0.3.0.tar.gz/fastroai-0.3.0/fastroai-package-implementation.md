# FastroAI Package Specification
## Version 1.0

**Status:** Final Design
**Target:** Standalone Python Package (PyPI)
**Dependencies:** pydantic, pydantic-ai
**Python:** ≥3.11

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Motivation & Problems Solved](#2-motivation--problems-solved)
3. [Design Philosophy](#3-design-philosophy)
4. [Package Scope](#4-package-scope)
5. [Architecture Overview](#5-architecture-overview)
6. [Core Module: Agent](#6-core-module-agent)
7. [Core Module: Pipelines](#7-core-module-pipelines)
8. [Core Module: Tools](#8-core-module-tools)
9. [Core Module: Usage](#9-core-module-usage)
10. [Core Module: Tracing](#10-core-module-tracing)
11. [Integration Patterns](#11-integration-patterns)
12. [Error Handling](#12-error-handling)
13. [Package Structure](#13-package-structure)
14. [Public API Surface](#14-public-api-surface)
15. [Implementation Plan](#15-implementation-plan)
16. [Appendices](#16-appendices)

---

## 1. Executive Summary

### 1.1 What Is FastroAI?

FastroAI is a **lightweight AI orchestration framework** built on PydanticAI. It provides:

1. **FastroAgent**: A convenience wrapper around PydanticAI's Agent with usage tracking and tracing
2. **Pipeline System**: Declarative DAG-based workflow orchestration for multi-step AI tasks
3. **Tool Safety**: Production-safe tool decorators with timeout and retry logic
4. **Cost Tracking**: Precise usage and cost calculation with microcents accuracy

### 1.2 The One-Sentence Pitch

> FastroAI lets you build production AI applications with PydanticAI while getting usage tracking, multi-step workflows, and production safety out of the box.

### 1.3 Who Is This For?

- Teams building AI-powered applications who want more than raw PydanticAI
- Projects needing multi-step AI workflows (extract → classify → transform → respond)
- Applications requiring usage tracking for billing or analytics
- Developers who want to avoid reinventing orchestration patterns

### 1.4 What Makes This Different?

| Approach | Limitation | FastroAI Solution |
|----------|------------|-------------------|
| Raw PydanticAI | No usage tracking, no workflows | Adds tracking + pipelines |
| LangChain/LlamaIndex | Heavy, opinionated, complex | Lightweight, composable |
| Custom code | Duplicated patterns, bugs | Battle-tested abstractions |
| Workflow engines (Temporal, Airflow) | Overkill for AI orchestration | Right-sized for AI tasks |

---

## 2. Motivation & Problems Solved

### 2.1 Problem: Every Project Reinvents the Same Patterns

**The Reality:**

Every team building AI applications ends up writing the same boilerplate:

```python
# Project A: Financial Calculator
class FinancialPipeline:
    def __init__(self):
        self.steps = []
        self.accumulated_data = {}

    def add_step(self, step):
        self.steps.append(step)  # ORDER MATTERS!

    async def execute(self, input_data):
        for step in self.steps:
            result = await step.execute(self.accumulated_data)
            self.accumulated_data.update(result)
        return self.accumulated_data

# Project B: Document Processor
class DocumentPipeline:
    def __init__(self):
        self.steps = []
        self.context = {}

    def add_step(self, step):
        self.steps.append(step)  # ORDER MATTERS!

    async def run(self, document):
        for step in self.steps:
            result = await step.process(self.context)
            self.context.update(result)
        return self.context

# Project C: Customer Support Bot
class SupportPipeline:
    # ... same pattern again ...
```

**The Problems:**
- Same logic duplicated across projects
- Bug fixes don't propagate
- Each implementation has subtle differences
- No parallelism (sequential execution only)
- No type safety (dict-based data passing)

**FastroAI Solution:**

```python
from fastro_ai import Pipeline, BaseStep, StepContext

pipeline = Pipeline(
    name="financial_calculator",
    steps={
        "extract": ExtractStep(),
        "classify": ClassifyStep(),
        "fetch_market": FetchMarketStep(),
        "fetch_user": FetchUserStep(),
        "calculate": CalculateStep(),
    },
    dependencies={
        "classify": ["extract"],
        "fetch_market": ["classify"],
        "fetch_user": ["classify"],      # Parallel with fetch_market!
        "calculate": ["fetch_market", "fetch_user"],
    },
)

result = await pipeline.execute(input_data, deps)
```

**What You Get:**
- ✅ Declarative dependencies (no manual ordering)
- ✅ Automatic parallelism (fetch_market and fetch_user run concurrently)
- ✅ Type-safe data passing via StepContext
- ✅ One implementation, tested and maintained

---

### 2.2 Problem: PydanticAI Doesn't Track Usage

**The Reality:**

PydanticAI is excellent for AI interactions, but it doesn't help with:
- How much did this conversation cost?
- How many tokens did we use?
- What's our billing for this user?

```python
# Raw PydanticAI
agent = Agent(model="openai:gpt-4o", system_prompt="...")
result = await agent.run("Hello!")

# result.output = "Hi there!"
# result.usage() = Usage(request_tokens=15, response_tokens=8, ...)

# But what's the cost? You have to calculate it yourself:
model_pricing = {"gpt-4o": {"input": 0.0025, "output": 0.01}}
# ... manual calculation ...
# ... handle model name normalization ...
# ... deal with floating point precision ...
```

**The Problems:**
- Manual cost calculation for each model
- Floating-point precision errors in billing
- No standard response format with usage data
- Tracing/observability is DIY

**FastroAI Solution:**

```python
from fastro_ai import FastroAgent

agent = FastroAgent(model="openai:gpt-4o")
response = await agent.run("Hello!")

# Everything you need in one response:
print(response.content)           # "Hi there!"
print(response.cost_microcents)   # 175 (integer, precise)
print(response.input_tokens)      # 15
print(response.output_tokens)     # 8
print(response.cost_dollars)      # 0.000175 (for display)
print(response.trace_id)          # "abc-123" (if tracing enabled)
```

**What You Get:**
- ✅ Automatic cost calculation with configurable pricing
- ✅ Microcents precision (no floating-point errors)
- ✅ Consistent `ChatResponse` format
- ✅ Built-in tracing support

---

### 2.3 Problem: Tools Crash Conversations

**The Reality:**

AI tools call external APIs that can fail:

```python
# Naive tool implementation
async def web_search(query: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.search.com?q={query}")
        return response.text

# What happens when:
# - API times out after 60 seconds?
# - API returns 500 error?
# - Network is down?

# The entire conversation crashes. User sees an error.
```

**The Problems:**
- Timeouts hang the conversation
- Exceptions crash the agent
- No retry logic for transient failures
- Poor user experience

**FastroAI Solution:**

```python
from fastro_ai.tools import safe_tool

@safe_tool(timeout=10, max_retries=3)
async def web_search(query: str) -> str:
    """Search the web for information."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.search.com?q={query}")
        return response.text

# Now when things fail:
# - Timeout after 10 seconds (not 60)
# - Retry up to 3 times with backoff
# - On final failure, return error message (not exception)
# - AI receives "Tool failed: Connection timeout" and responds gracefully
```

**What You Get:**
- ✅ Timeout protection (configurable per tool)
- ✅ Automatic retry with exponential backoff
- ✅ Graceful degradation (errors become messages)
- ✅ Conversation continues even when tools fail

---

### 2.4 Problem: Multi-Turn Conversations Are Complex

**The Reality:**

Gathering information across multiple turns requires careful state management:

```python
# Turn 1: "I want to invest"
# → Need: amount, risk tolerance, time horizon
# → Have: nothing
# → Response: "How much would you like to invest?"

# Turn 2: "50 thousand"
# → Need: risk tolerance, time horizon
# → Have: amount=$50,000
# → Response: "What's your risk tolerance?"

# Turn 3: "Medium risk, 10 years"
# → Need: nothing
# → Have: amount=$50,000, risk=medium, horizon=10
# → NOW run expensive calculation
```

**The Problems:**
- When do we have enough info to proceed?
- How do we avoid re-running expensive steps?
- How do we signal "need more info" vs "ready to proceed"?
- State management across turns

**FastroAI Solution:**

```python
from fastro_ai import Pipeline, ConversationState, ConversationStatus

class GatherInfoStep(AgentStep[MyDeps, ConversationState[InvestmentInfo]]):
    async def execute(self, context: StepContext[MyDeps]) -> ConversationState[InvestmentInfo]:
        info = await self._extract_info(context.get_input("message"))

        if info.is_complete():
            return ConversationState(status=ConversationStatus.COMPLETE, data=info)

        return ConversationState(
            status=ConversationStatus.INCOMPLETE,
            data=info,
            context={"missing": info.missing_fields()},
        )

class ExpensiveCalculationStep(AgentStep[MyDeps, InvestmentPlan]):
    # Only runs when GatherInfoStep returns COMPLETE
    async def execute(self, context: StepContext[MyDeps]) -> InvestmentPlan:
        info = context.get_dependency("gather").data
        return await self._calculate(info)

pipeline = Pipeline(
    steps={"gather": GatherInfoStep(), "calculate": ExpensiveCalculationStep()},
    dependencies={"calculate": ["gather"]},
)

# Turn 1
result = await pipeline.execute({"message": "I want to invest"}, deps)
# result.stopped_early = True
# result.conversation_state.status = INCOMPLETE
# result.conversation_state.context = {"missing": ["amount", "risk", "horizon"]}

# Turn 2 (after user provides more info)
result = await pipeline.execute({"message": "50k, medium risk, 10 years"}, deps)
# result.stopped_early = False
# result.output = InvestmentPlan(...)
```

**What You Get:**
- ✅ Clear COMPLETE/INCOMPLETE signaling
- ✅ Expensive steps only run when ready
- ✅ Partial data preserved across turns
- ✅ Context for what's missing

---

### 2.5 Problem: No Visibility Into What's Happening

**The Reality:**

When something goes wrong in production:
- Which step failed?
- How long did each step take?
- What was the total cost?
- How do I correlate logs?

```python
# Without tracing
result = await some_complex_operation()
# Something failed. Good luck debugging.
```

**FastroAI Solution:**

```python
from fastro_ai import Pipeline, SimpleTracer

tracer = SimpleTracer()

result = await pipeline.execute(input_data, deps, tracer=tracer)

# Logs show:
# [abc-123] Starting pipeline.investment_advisor
# [abc-124] Starting step.extract
# [abc-124] Completed step.extract in 0.234s
# [abc-125] Starting step.classify
# [abc-125] Completed step.classify in 0.567s
# [abc-126] Starting step.fetch_market  ─┐
# [abc-127] Starting step.fetch_user    ─┼─ Parallel!
# [abc-126] Completed step.fetch_market ─┘
# [abc-127] Completed step.fetch_user
# [abc-128] Starting step.calculate
# [abc-128] Completed step.calculate in 1.234s
# [abc-123] Completed pipeline.investment_advisor in 2.456s

# Plus usage breakdown:
print(result.usage.steps)
# {
#   "extract": StepUsage(cost_microcents=150, ...),
#   "classify": StepUsage(cost_microcents=200, ...),
#   "calculate": StepUsage(cost_microcents=500, ...),
# }
```

**What You Get:**
- ✅ Trace IDs for correlation
- ✅ Per-step timing
- ✅ Per-step usage breakdown
- ✅ Parallel execution visibility
- ✅ Pluggable tracer (use Logfire, OpenTelemetry, etc.)

---

### 2.6 Summary: Before vs After

| Concern | Before FastroAI | With FastroAI |
|---------|-----------------|---------------|
| **Multi-step workflows** | Manual ordering, sequential | Declarative deps, auto-parallel |
| **Usage tracking** | DIY calculation | Built into ChatResponse |
| **Cost precision** | Floating-point errors | Integer microcents |
| **Tool failures** | Crash conversation | Graceful degradation |
| **Multi-turn state** | Manual state machine | ConversationState pattern |
| **Observability** | Add logging everywhere | Built-in tracing |
| **Type safety** | Dict-based, typos at runtime | Generic types, IDE support |
| **Code duplication** | Same patterns in every project | Shared, tested abstractions |

---

## 3. Design Philosophy

### 3.1 Framework, Not Application

FastroAI provides **orchestration primitives**. It does not:

| FastroAI Provides | Application Provides |
|-------------------|---------------------|
| `ChatResponse` with usage data | Persisting usage to database |
| `message_history` parameter | Loading/storing conversation history |
| `Tracer` protocol | Logfire/OpenTelemetry integration |
| `Pipeline` execution | API endpoints, authentication |
| Cost calculation | Billing integration |

**Why This Matters:**

```python
# FastroAI returns data. You decide what to do with it.
response = await agent.run("Hello")

# Store in PostgreSQL? Redis? DynamoDB? Your choice.
await my_storage.save(response.cost_microcents)

# Bill via Stripe? Internal system? Your choice.
await my_billing.charge(user_id, response.cost_microcents)
```

### 3.2 Composition Over Configuration

Components are **injected**, not configured via hidden settings:

```python
# ❌ Bad: Hidden configuration
agent = FastroAgent()  # Reads from settings.AI_MODEL_PRICING somewhere

# ✅ Good: Explicit injection
pricing = {"gpt-4o": {"input_cost_per_1k_tokens": 250, ...}}
calculator = CostCalculator(pricing=pricing)
agent = FastroAgent(cost_calculator=calculator)
```

**Why This Matters:**
- No magic, no surprises
- Easy to test (inject mocks)
- Clear dependencies
- Works in any environment

### 3.3 Type Safety Throughout

Every public API is fully typed with generics:

```python
# Types flow through the pipeline
class ExtractStep(BaseStep[MyDeps, ExtractionResult]):
    async def execute(self, context: StepContext[MyDeps]) -> ExtractionResult:
        # IDE knows:
        # - context.deps is MyDeps
        # - Return type must be ExtractionResult
        ...

class ClassifyStep(BaseStep[MyDeps, Classification]):
    async def execute(self, context: StepContext[MyDeps]) -> Classification:
        # Type-safe dependency access
        extraction: ExtractionResult = context.get_dependency("extract", ExtractionResult)
        # IDE autocompletes extraction.entities, extraction.text, etc.
        ...
```

### 3.4 Escape Hatches Available

FastroAI wraps PydanticAI, not replaces it:

```python
# Use FastroAgent for convenience
agent = FastroAgent(model="gpt-4o")

# Or inject your own PydanticAI agent
from pydantic_ai import Agent
custom_agent = Agent(model="gpt-4o", result_type=MyStructuredOutput)
agent = FastroAgent(agent=custom_agent)

# Or use PydanticAI directly when FastroAI doesn't fit
from pydantic_ai import Agent
agent = Agent(...)  # Full control
```

---

## 4. Package Scope

### 4.1 What's Included

| Component | Purpose | Problem Solved |
|-----------|---------|----------------|
| `FastroAgent` | PydanticAI wrapper | Usage tracking, consistent response format |
| `ChatResponse` | Response model | Standardized output with cost/tokens/trace |
| `Pipeline` | DAG orchestrator | Multi-step workflows with parallelism |
| `BaseStep` | Step abstraction | Type-safe, testable workflow steps |
| `AgentStep` | Step + agent | Convenience for AI-powered steps |
| `ConversationState` | Multi-turn signal | Pause/resume workflows |
| `BasePipeline` | Router | A/B testing, complexity routing |
| `CostCalculator` | Cost calculation | Precise billing in microcents |
| `@safe_tool` | Tool decorator | Timeout, retry, error handling |
| `Tracer` | Observability | Distributed tracing protocol |

### 4.2 What's Excluded (And Why)

| Concern | Why Excluded | What You Do |
|---------|--------------|-------------|
| Database access | Framework-agnostic | Use SQLAlchemy, Tortoise, etc. |
| User/account models | Application domain | Define your own models |
| Memory persistence | Storage-agnostic | Implement MessageReader/Writer |
| Usage persistence | Billing is app logic | Call your billing service |
| Settings management | No hidden config | Use Pydantic Settings |
| Logfire integration | Optional dependency | Implement LogfireTracer |
| HTTP transport | Not a web framework | Use FastAPI, Starlette |

### 4.3 Dependencies

```toml
[project]
dependencies = [
    "pydantic>=2.0",
    "pydantic-ai>=0.1.0",
]

[project.optional-dependencies]
logfire = ["logfire>=1.0"]
```

**Why So Few Dependencies?**
- Fewer conflicts
- Faster installs
- Easier auditing
- Your choice of HTTP client, ORM, etc.

---

## 5. Architecture Overview

### 5.1 Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                          │
│  FastAPI endpoints, database operations, authentication      │
│  Memory services, usage persistence, billing integration     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTROAI PACKAGE                          │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    PIPELINES                         │    │
│  │  Declarative workflows, parallel execution,          │    │
│  │  multi-turn conversations, routing                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│                              │ orchestrates                  │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                      AGENT                           │    │
│  │  PydanticAI wrapper, usage tracking,                 │    │
│  │  consistent response format                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                              │                               │
│          ┌───────────────────┼───────────────────┐          │
│          ▼                   ▼                   ▼          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │    TOOLS    │     │    USAGE    │     │   TRACING   │    │
│  │  @safe_tool │     │ Calculator  │     │   Protocol  │    │
│  │  Toolsets   │     │ Microcents  │     │   Simple    │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ wraps
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      PYDANTIC AI                             │
│  The foundation: Agent, tools, model abstraction             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow: Single Agent Call

```
User Message
    │
    ▼
FastroAgent.run(message, deps, message_history, tracer)
    │
    ├─► Tracer.span("fastro_agent.run")
    │       └─► Creates trace context
    │
    ├─► PydanticAI Agent.run(user_prompt, message_history, ...)
    │       │
    │       ├─► Tool calls (if any)
    │       │       └─► @safe_tool handles timeout/retry
    │       │
    │       └─► Model response with usage stats
    │
    ├─► CostCalculator.calculate_cost(model, input_tokens, output_tokens)
    │       └─► Returns cost in microcents (integer)
    │
    └─► ChatResponse
            ├─► content: "Hello! How can I help?"
            ├─► cost_microcents: 175
            ├─► input_tokens: 15
            ├─► output_tokens: 8
            ├─► tool_calls: [...]
            └─► trace_id: "abc-123"
```

### 5.3 Data Flow: Pipeline Execution

```
Input Data + Dependencies
    │
    ▼
Pipeline.execute(input_data, deps, tracer)
    │
    ├─► Tracer.span("pipeline.{name}")
    │
    ├─► Topological sort: [[a], [b, c], [d]]
    │       └─► Groups steps by execution level
    │
    ├─► Level 0: Execute [step_a]
    │       │
    │       └─► step_a.execute(context)
    │               ├─► context.get_input("document")
    │               ├─► Run AI/logic
    │               └─► Return typed output
    │
    ├─► Level 1: Execute [step_b, step_c] IN PARALLEL
    │       │
    │       ├─► asyncio.gather(step_b.execute(...), step_c.execute(...))
    │       │
    │       └─► Both complete before Level 2
    │
    ├─► Level 2: Execute [step_d]
    │       │
    │       └─► step_d.execute(context)
    │               ├─► context.get_dependency("b", TypeB)
    │               ├─► context.get_dependency("c", TypeC)
    │               └─► Return final output
    │
    ├─► Collect usage from all steps
    │
    └─► PipelineResult
            ├─► output: step_d's output
            ├─► step_outputs: {"a": ..., "b": ..., "c": ..., "d": ...}
            ├─► usage: PipelineUsage(total_cost_microcents=850, steps={...})
            └─► stopped_early: False
```

### 5.4 Data Flow: Multi-Turn Conversation

```
Turn 1: "I want to invest"
    │
    ▼
Pipeline.execute({"message": "I want to invest"}, deps)
    │
    ├─► GatherInfoStep.execute(context)
    │       │
    │       ├─► Extract info from message
    │       │       └─► amount=None, risk=None, horizon=None
    │       │
    │       └─► Return ConversationState(
    │               status=INCOMPLETE,
    │               data=InvestmentInfo(amount=None, ...),
    │               context={"missing": ["amount", "risk", "horizon"]}
    │           )
    │
    ├─► Pipeline sees INCOMPLETE status
    │       └─► STOPS EXECUTION (doesn't run CalculateStep)
    │
    └─► PipelineResult
            ├─► output: None (didn't reach final step)
            ├─► stopped_early: True
            ├─► conversation_state: ConversationState(INCOMPLETE, ...)
            └─► usage: (only GatherInfoStep's usage)

Turn 2: "50k, medium risk, 10 years"
    │
    ▼
Pipeline.execute({"message": "50k, medium risk, 10 years"}, deps)
    │
    ├─► GatherInfoStep.execute(context)
    │       │
    │       └─► Return ConversationState(
    │               status=COMPLETE,
    │               data=InvestmentInfo(amount=50000, risk="medium", horizon=10)
    │           )
    │
    ├─► Pipeline sees COMPLETE status
    │       └─► CONTINUES to CalculateStep
    │
    ├─► CalculateStep.execute(context)
    │       │
    │       ├─► info = context.get_dependency("gather").data
    │       │
    │       └─► Return InvestmentPlan(...)
    │
    └─► PipelineResult
            ├─► output: InvestmentPlan(...)
            ├─► stopped_early: False
            └─► usage: (both steps' usage)
```

---

## 6. Core Module: Agent

### 6.1 The Problem Agent Solves

**Without FastroAgent:**

```python
from pydantic_ai import Agent

agent = Agent(model="openai:gpt-4o", system_prompt="...")
result = await agent.run("Hello")

# Now you need to:
# 1. Extract content
content = result.output

# 2. Get usage
usage = result.usage()
input_tokens = usage.request_tokens
output_tokens = usage.response_tokens

# 3. Calculate cost (manually!)
pricing = {
    "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000}
}
model = usage.model or "gpt-4o"  # Might be None!
normalized_model = model.split(":")[-1].lower()  # Handle "openai:gpt-4o"
cost = (input_tokens * pricing[normalized_model]["input"] +
        output_tokens * pricing[normalized_model]["output"])
# WARNING: Floating point! $0.000001 errors compound!

# 4. Add tracing (more boilerplate)
# 5. Handle streaming (even more boilerplate)
# 6. Repeat in every project
```

**With FastroAgent:**

```python
from fastro_ai import FastroAgent

agent = FastroAgent(model="openai:gpt-4o")
response = await agent.run("Hello")

# Everything you need:
response.content           # "Hi there!"
response.cost_microcents   # 175 (precise integer)
response.input_tokens      # 15
response.output_tokens     # 8
response.trace_id          # "abc-123"
response.cost_dollars      # 0.000175 (for display)
```

### 6.2 AgentConfig

```python
from pydantic import BaseModel, Field

# Package-level defaults
DEFAULT_MODEL = "openai:gpt-4o"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_MAX_RETRIES = 3
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant."


class AgentConfig(BaseModel):
    """Configuration for FastroAgent instances.

    All parameters have sensible defaults. Override as needed.

    Example:
        # Minimal
        config = AgentConfig()

        # Custom
        config = AgentConfig(
            model="anthropic:claude-3-5-sonnet",
            system_prompt="You are a financial advisor.",
            temperature=0.3,
        )

        # Use with agent
        agent = FastroAgent(config=config)

        # Or pass kwargs directly
        agent = FastroAgent(model="openai:gpt-4o-mini", temperature=0.5)
    """

    model: str = DEFAULT_MODEL
    system_prompt: str | None = None
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=2.0)
    timeout_seconds: int = Field(default=DEFAULT_TIMEOUT_SECONDS, gt=0)
    max_retries: int = Field(default=DEFAULT_MAX_RETRIES, ge=0)

    def get_effective_system_prompt(self) -> str:
        """Get system prompt, using default if not set."""
        return self.system_prompt if self.system_prompt is not None else DEFAULT_SYSTEM_PROMPT
```

### 6.3 ChatResponse

```python
from typing import Any
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Response from an AI agent interaction.

    Contains the response plus comprehensive usage metrics for
    billing, analytics, and debugging.

    Attributes:
        content: The AI's response text.
        model: Model that generated the response.
        input_tokens: Tokens consumed by input.
        output_tokens: Tokens in response.
        total_tokens: input + output.
        tool_calls: Tools invoked during generation.
        cost_microcents: Cost in 1/10,000ths of a cent.
        processing_time_ms: Wall-clock time.
        trace_id: Distributed tracing correlation ID.

    Example:
        response = await agent.run("What is 2+2?")

        print(f"Answer: {response.content}")
        print(f"Cost: ${response.cost_dollars:.6f}")
        print(f"Tokens: {response.total_tokens}")

        if response.tool_calls:
            for call in response.tool_calls:
                print(f"Used tool: {call['tool_name']}")

    Why Microcents?
        Floating-point math has precision errors:
        >>> 0.1 + 0.2
        0.30000000000000004

        With microcents (integers), precision is exact:
        >>> 100 + 200
        300

        For billing systems, this matters.
    """

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    tool_calls: list[dict[str, Any]] = []
    cost_microcents: int
    processing_time_ms: int
    trace_id: str | None = None

    @property
    def cost_dollars(self) -> float:
        """Cost in dollars for display. Use cost_microcents for calculations."""
        return self.cost_microcents / 1_000_000
```

### 6.4 StreamChunk

```python
class StreamChunk(BaseModel):
    """A chunk in a streaming response.

    Most chunks have content with is_final=False.
    The last chunk has is_final=True with complete usage data.

    Example:
        async for chunk in agent.run_stream("Tell me a story"):
            if chunk.is_final:
                print(f"\\nCost: ${chunk.usage_data.cost_dollars:.6f}")
            else:
                print(chunk.content, end="", flush=True)
    """

    content: str = ""
    is_final: bool = False
    usage_data: ChatResponse | None = None
```

### 6.5 FastroAgent

```python
from __future__ import annotations
import time
from collections.abc import AsyncGenerator
from typing import Any, TypeVar

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.settings import ModelSettings
from pydantic_ai.toolsets import AbstractToolset

from ..tracing import Tracer, NoOpTracer
from ..usage import CostCalculator
from .schemas import AgentConfig, ChatResponse, StreamChunk

T = TypeVar("T")


class FastroAgent:
    """AI agent with usage tracking, cost calculation, and tracing.

    Wraps PydanticAI's Agent to provide:
    - Automatic cost calculation
    - Optional distributed tracing
    - Streaming and non-streaming modes
    - Consistent ChatResponse format

    The agent is STATELESS regarding conversation history.
    Callers load history and pass it to run().

    Example:
        # Basic usage
        agent = FastroAgent(
            model="openai:gpt-4o",
            system_prompt="You are helpful.",
        )
        response = await agent.run("Hello!")

        # With conversation history (you load it)
        history = await my_memory_service.load(user_id)
        response = await agent.run("Continue", message_history=history)

        # With tracing
        tracer = SimpleTracer()
        response = await agent.run("Hello", tracer=tracer)

        # With custom deps for tools
        response = await agent.run("Search for news", deps=MyDeps(api_key="..."))
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        agent: Agent | None = None,
        toolsets: list[AbstractToolset] | None = None,
        cost_calculator: CostCalculator | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize FastroAgent.

        Args:
            config: Agent configuration. If None, creates from kwargs.
            agent: Pre-configured PydanticAI Agent (escape hatch).
            toolsets: Tool sets available to the agent.
            cost_calculator: Cost calculator. Default uses standard pricing.
            **kwargs: Passed to AgentConfig if config is None.

        Example:
            # Config object
            agent = FastroAgent(config=AgentConfig(model="gpt-4o"))

            # Kwargs
            agent = FastroAgent(model="gpt-4o", temperature=0.5)

            # Custom pricing
            calc = CostCalculator(pricing=my_pricing)
            agent = FastroAgent(cost_calculator=calc)

            # Escape hatch: your own PydanticAI agent
            pydantic_agent = Agent(model="gpt-4o", result_type=MyType)
            agent = FastroAgent(agent=pydantic_agent)
        """
        self.config = config or AgentConfig(**kwargs)
        self.toolsets = toolsets or []
        self.cost_calculator = cost_calculator or CostCalculator()

        if agent is not None:
            self.agent = agent
        else:
            self.agent = Agent(
                model=self.config.model,
                system_prompt=self.config.get_effective_system_prompt(),
                toolsets=self.toolsets,
            )

    async def run(
        self,
        message: str,
        deps: T | None = None,
        message_history: list[ModelMessage] | None = None,
        model_settings: ModelSettings | None = None,
        tracer: Tracer | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Execute a single agent interaction.

        Args:
            message: User message to send.
            deps: Dependencies passed to tools. Can be any type.
            message_history: Previous messages (you load these).
            model_settings: Runtime model config overrides.
            tracer: Tracer for distributed tracing.
            **kwargs: Passed to PydanticAI Agent.run().

        Returns:
            ChatResponse with content, usage, cost, and trace_id.

        Example:
            # Simple
            response = await agent.run("Hello!")

            # With history
            history = await memory.load(user_id)
            response = await agent.run("Continue", message_history=history)
            await memory.save(user_id, message, response.content)
        """
        effective_tracer = tracer or NoOpTracer()

        async with effective_tracer.span(
            "fastro_agent.run",
            model=self.config.model,
            has_history=message_history is not None,
        ) as trace_id:
            return await self._execute(
                message=message,
                deps=deps,
                message_history=message_history,
                model_settings=model_settings,
                trace_id=trace_id,
                **kwargs,
            )

    async def run_stream(
        self,
        message: str,
        deps: T | None = None,
        message_history: list[ModelMessage] | None = None,
        model_settings: ModelSettings | None = None,
        tracer: Tracer | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Execute a streaming agent interaction.

        Yields StreamChunk objects. Final chunk has usage data.

        Example:
            async for chunk in agent.run_stream("Tell a story"):
                if chunk.is_final:
                    print(f"\\nCost: ${chunk.usage_data.cost_dollars:.6f}")
                else:
                    print(chunk.content, end="")
        """
        effective_tracer = tracer or NoOpTracer()

        async with effective_tracer.span(
            "fastro_agent.run_stream",
            model=self.config.model,
        ) as trace_id:
            async for chunk in self._execute_stream(
                message=message,
                deps=deps,
                message_history=message_history,
                model_settings=model_settings,
                trace_id=trace_id,
                **kwargs,
            ):
                yield chunk

    async def _execute(
        self,
        message: str,
        deps: T | None,
        message_history: list[ModelMessage] | None,
        model_settings: ModelSettings | None,
        trace_id: str,
        **kwargs: Any,
    ) -> ChatResponse:
        """Internal execution logic."""
        effective_settings = model_settings or ModelSettings(
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        start_time = time.perf_counter()

        result = await self.agent.run(
            user_prompt=message,
            deps=deps,
            message_history=message_history,
            model_settings=effective_settings,
            **kwargs,
        )

        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        return self._create_response(result, trace_id, processing_time_ms)

    async def _execute_stream(
        self,
        message: str,
        deps: T | None,
        message_history: list[ModelMessage] | None,
        model_settings: ModelSettings | None,
        trace_id: str,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Internal streaming logic."""
        effective_settings = model_settings or ModelSettings(
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        start_time = time.perf_counter()

        async with self.agent.run_stream(
            user_prompt=message,
            deps=deps,
            message_history=message_history,
            model_settings=effective_settings,
            **kwargs,
        ) as response:
            async for text_chunk in response.stream_text():
                yield StreamChunk(content=text_chunk, is_final=False)

            final_result = await response.get_output()
            processing_time_ms = int((time.perf_counter() - start_time) * 1000)

            final_response = self._create_response(
                final_result, trace_id, processing_time_ms
            )
            yield StreamChunk(content="", is_final=True, usage_data=final_response)

    def _create_response(
        self,
        result: Any,
        trace_id: str,
        processing_time_ms: int,
    ) -> ChatResponse:
        """Create ChatResponse from PydanticAI result."""
        usage = result.usage()
        model = getattr(usage, "model", self.config.model) or self.config.model
        input_tokens = usage.request_tokens or 0
        output_tokens = usage.response_tokens or 0

        cost_microcents = self.cost_calculator.calculate_cost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        tool_calls = self._extract_tool_calls(result)

        content = result.output if isinstance(result.output, str) else str(result.output)

        return ChatResponse(
            content=content,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=usage.total_tokens or 0,
            tool_calls=tool_calls,
            cost_microcents=cost_microcents,
            processing_time_ms=processing_time_ms,
            trace_id=trace_id,
        )

    def _extract_tool_calls(self, result: Any) -> list[dict[str, Any]]:
        """Extract tool call info from result."""
        tool_calls = []

        for message in result.new_messages():
            if hasattr(message, "parts"):
                for part in message.parts:
                    if hasattr(part, "tool_name") and hasattr(part, "args"):
                        tool_calls.append({
                            "tool_name": part.tool_name,
                            "args": part.args,
                            "tool_call_id": getattr(part, "tool_call_id", None),
                        })

        return tool_calls
```

---

## 7. Core Module: Pipelines

### 7.1 The Problem Pipelines Solve

**Without Pipelines:**

```python
# Manual orchestration - error-prone, no parallelism
async def process_document(document, deps):
    # Step 1: Extract
    extraction = await extract_step.execute(document)

    # Step 2: Classify (needs extraction)
    classification = await classify_step.execute(extraction)

    # Step 3 & 4: Fetch data (could run in parallel, but don't)
    market_data = await fetch_market_step.execute(classification)
    user_data = await fetch_user_step.execute(classification)  # Wasted time!

    # Step 5: Calculate (needs both)
    result = await calculate_step.execute(market_data, user_data)

    return result

# Problems:
# - fetch_market and fetch_user run sequentially (slow!)
# - Adding/removing steps requires manual reordering
# - No type safety between steps
# - No usage tracking across steps
# - No tracing
```

**With Pipelines:**

```python
from fastro_ai import Pipeline, BaseStep, StepContext

pipeline = Pipeline(
    name="document_processor",
    steps={
        "extract": ExtractStep(),
        "classify": ClassifyStep(),
        "fetch_market": FetchMarketStep(),
        "fetch_user": FetchUserStep(),
        "calculate": CalculateStep(),
    },
    dependencies={
        "classify": ["extract"],
        "fetch_market": ["classify"],
        "fetch_user": ["classify"],      # Parallel with fetch_market!
        "calculate": ["fetch_market", "fetch_user"],
    },
)

result = await pipeline.execute({"document": doc}, deps, tracer)

# Benefits:
# - fetch_market and fetch_user run in parallel automatically
# - Type-safe dependency access
# - Usage tracking aggregated
# - Distributed tracing
# - Easy to add/remove/reorder steps
```

### 7.2 Pipeline Schemas

```python
from pydantic import BaseModel


class StepUsage(BaseModel):
    """Usage metrics for a single pipeline step.

    Automatically extracted from ChatResponse when using AgentStep.
    """

    input_tokens: int = 0
    output_tokens: int = 0
    cost_microcents: int = 0
    processing_time_ms: int = 0
    model: str | None = None

    @classmethod
    def from_chat_response(cls, response: ChatResponse) -> "StepUsage":
        """Create from ChatResponse."""
        return cls(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_microcents=response.cost_microcents,
            processing_time_ms=response.processing_time_ms,
            model=response.model,
        )

    def __add__(self, other: "StepUsage") -> "StepUsage":
        """Add two usages (for steps with multiple AI calls)."""
        return StepUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cost_microcents=self.cost_microcents + other.cost_microcents,
            processing_time_ms=self.processing_time_ms + other.processing_time_ms,
            model=self.model or other.model,
        )


class PipelineUsage(BaseModel):
    """Aggregated usage across all pipeline steps."""

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_microcents: int = 0
    total_processing_time_ms: int = 0
    steps: dict[str, StepUsage] = {}

    @classmethod
    def from_step_usages(cls, step_usages: dict[str, StepUsage]) -> "PipelineUsage":
        """Aggregate from individual step usages."""
        return cls(
            total_input_tokens=sum(u.input_tokens for u in step_usages.values()),
            total_output_tokens=sum(u.output_tokens for u in step_usages.values()),
            total_cost_microcents=sum(u.cost_microcents for u in step_usages.values()),
            total_processing_time_ms=sum(u.processing_time_ms for u in step_usages.values()),
            steps=step_usages,
        )

    @property
    def total_cost_dollars(self) -> float:
        """Total cost in dollars for display."""
        return self.total_cost_microcents / 1_000_000
```

### 7.3 Base Abstractions

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")
T = TypeVar("T")


class ConversationStatus(str, Enum):
    """Status of multi-turn conversation gathering."""

    COMPLETE = "complete"      # All info gathered, proceed
    INCOMPLETE = "incomplete"  # Need more info, pause pipeline


class ConversationState(BaseModel, Generic[T]):
    """Signal for multi-turn conversation steps.

    When a step returns ConversationState with INCOMPLETE status,
    the pipeline stops early. Partial data and context are preserved.

    Example:
        class GatherInfoStep(BaseStep[MyDeps, ConversationState[UserInfo]]):
            async def execute(self, context) -> ConversationState[UserInfo]:
                info = await self._extract(context.get_input("message"))

                if info.is_complete():
                    return ConversationState(
                        status=ConversationStatus.COMPLETE,
                        data=info,
                    )

                return ConversationState(
                    status=ConversationStatus.INCOMPLETE,
                    data=info,  # Partial data
                    context={"missing": info.missing_fields()},
                )
    """

    status: ConversationStatus
    data: T | None = None
    context: dict[str, Any] = {}


class StepContext(Generic[DepsT]):
    """Execution context provided to pipeline steps.

    Provides access to:
    - Pipeline inputs (the data passed to execute())
    - Outputs from dependency steps
    - Application dependencies (your db session, user, etc.)
    - Tracer for custom spans

    Example:
        class ProcessStep(BaseStep[MyDeps, Result]):
            async def execute(self, context: StepContext[MyDeps]) -> Result:
                # Get pipeline input
                document = context.get_input("document")

                # Get output from dependency step
                classification = context.get_dependency("classify", Classification)

                # Access your deps
                db = context.deps.session
                user_id = context.deps.user_id

                # Custom tracing
                if context.tracer:
                    async with context.tracer.span("custom_operation"):
                        result = await process(document)

                return result
    """

    def __init__(
        self,
        step_id: str,
        inputs: dict[str, Any],
        deps: DepsT,
        step_outputs: dict[str, Any],
        tracer: Tracer | None = None,
    ) -> None:
        self._step_id = step_id
        self._inputs = inputs
        self._deps = deps
        self._outputs = step_outputs
        self._tracer = tracer

    @property
    def step_id(self) -> str:
        """Current step's ID."""
        return self._step_id

    @property
    def deps(self) -> DepsT:
        """Application dependencies (your session, user, etc.)."""
        return self._deps

    @property
    def tracer(self) -> Tracer | None:
        """Tracer for custom spans."""
        return self._tracer

    def get_input(self, key: str, default: Any = None) -> Any:
        """Get value from pipeline inputs."""
        return self._inputs.get(key, default)

    def get_dependency(
        self,
        step_id: str,
        output_type: Type[T] | None = None,
    ) -> T:
        """Get output from a dependency step.

        Args:
            step_id: ID of the dependency step.
            output_type: Expected type (for IDE/type checker).

        Raises:
            ValueError: If step_id not in dependencies or hasn't run.

        Example:
            # With type hint (IDE knows extraction is ExtractionResult)
            extraction = context.get_dependency("extract", ExtractionResult)
            extraction.entities  # Autocomplete works!
        """
        if step_id not in self._outputs:
            raise ValueError(
                f"Step '{step_id}' not a dependency of '{self._step_id}' "
                f"or hasn't completed. Available: {list(self._outputs.keys())}"
            )
        return self._outputs[step_id]

    def get_dependency_or_none(
        self,
        step_id: str,
        output_type: Type[T] | None = None,
    ) -> T | None:
        """Get output or None if not available. For optional deps."""
        return self._outputs.get(step_id)


class BaseStep(ABC, Generic[DepsT, OutputT]):
    """Abstract base class for pipeline steps.

    A step is one unit of work. It:
    - Receives context with inputs and dependencies
    - Does something (AI call, computation, API call)
    - Returns typed output

    Steps should be stateless. Any state goes in deps or inputs.

    Example:
        class ExtractStep(BaseStep[MyDeps, ExtractionResult]):
            '''Extract entities from document.'''

            def __init__(self):
                self.agent = FastroAgent(system_prompt="Extract entities.")

            async def execute(self, context: StepContext[MyDeps]) -> ExtractionResult:
                document = context.get_input("document")
                response = await self.agent.run(f"Extract: {document}")
                return ExtractionResult.model_validate_json(response.content)
    """

    @abstractmethod
    async def execute(self, context: StepContext[DepsT]) -> OutputT:
        """Execute step logic. Return typed output."""
        ...
```

### 7.4 AgentStep

```python
from abc import abstractmethod
from typing import Any, TypeVar

from pydantic_ai.messages import ModelMessage
from pydantic_ai.toolsets import AbstractToolset

from ..agent import FastroAgent, AgentConfig, ChatResponse
from ..usage import CostCalculator
from .base import BaseStep, StepContext
from .schemas import StepUsage

DepsT = TypeVar("DepsT")
OutputT = TypeVar("OutputT")


class AgentStep(BaseStep[DepsT, OutputT]):
    """Base class for steps using FastroAgent.

    Provides:
    - Pre-configured FastroAgent
    - run_agent() method that forwards context
    - Automatic usage tracking

    Example:
        class ClassifyStep(AgentStep[MyDeps, Classification]):
            def __init__(self):
                super().__init__(
                    system_prompt="Classify input. Return JSON.",
                    temperature=0.0,  # Deterministic
                )

            async def execute(self, context: StepContext[MyDeps]) -> Classification:
                text = context.get_dependency("extract", ExtractionResult).text

                response = await self.run_agent(context, f"Classify: {text}")

                return Classification.model_validate_json(response.content)
    """

    def __init__(
        self,
        system_prompt: str,
        model: str = "openai:gpt-4o",
        toolsets: list[AbstractToolset] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        cost_calculator: CostCalculator | None = None,
    ) -> None:
        """Initialize AgentStep.

        Args:
            system_prompt: System prompt for the agent.
            model: Model identifier.
            toolsets: Tools available to this step.
            temperature: Sampling temperature.
            max_tokens: Max response tokens.
            cost_calculator: Custom cost calculator.
        """
        self.agent = FastroAgent(
            config=AgentConfig(
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            toolsets=toolsets,
            cost_calculator=cost_calculator,
        )
        self._last_usage: StepUsage | None = None

    @property
    def last_usage(self) -> StepUsage | None:
        """Usage from most recent run_agent() call."""
        return self._last_usage

    async def run_agent(
        self,
        context: StepContext[DepsT],
        message: str,
        message_history: list[ModelMessage] | None = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Run agent with context forwarding.

        Automatically:
        - Passes context.deps to agent
        - Passes context.tracer for tracing
        - Records usage in self.last_usage
        """
        response = await self.agent.run(
            message=message,
            deps=context.deps,
            message_history=message_history,
            tracer=context.tracer,
            **kwargs,
        )

        self._last_usage = StepUsage.from_chat_response(response)

        return response

    @abstractmethod
    async def execute(self, context: StepContext[DepsT]) -> OutputT:
        """Implement step logic using self.run_agent()."""
        ...
```

### 7.5 Pipeline Executor

```python
from __future__ import annotations
import asyncio
from typing import Any, TypeVar

from .base import BaseStep, ConversationState, ConversationStatus, StepContext
from .agent_step import AgentStep
from .schemas import StepUsage

DepsT = TypeVar("DepsT")


class StepExecutionError(Exception):
    """Raised when a pipeline step fails."""

    def __init__(self, step_id: str, original_error: Exception) -> None:
        self.step_id = step_id
        self.original_error = original_error
        super().__init__(f"Step '{step_id}' failed: {original_error}")


class ExecutionResult:
    """Internal execution result before conversion to PipelineResult."""

    def __init__(self) -> None:
        self.outputs: dict[str, Any] = {}
        self.usages: dict[str, StepUsage] = {}
        self.conversation_state: ConversationState | None = None
        self.stopped_early: bool = False


class PipelineExecutor:
    """DAG executor with parallelism and early termination.

    Internal class - use Pipeline for the public API.
    """

    def __init__(
        self,
        steps: dict[str, BaseStep],
        dependencies: dict[str, list[str]],
    ) -> None:
        self.steps = steps
        self.dependencies = dependencies
        self._validate()
        self._execution_levels = self._topological_sort()

    def _validate(self) -> None:
        """Validate step graph."""
        # Check references
        for step_id, deps in self.dependencies.items():
            if step_id not in self.steps:
                raise ValueError(f"Dependency for unknown step: '{step_id}'")
            for dep in deps:
                if dep not in self.steps:
                    raise ValueError(f"Step '{step_id}' depends on unknown: '{dep}'")

        # Check cycles
        visited = set()
        rec_stack = set()

        def has_cycle(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)

            for dep in self.dependencies.get(step_id, []):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(step_id)
            return False

        for step_id in self.steps:
            if step_id not in visited:
                if has_cycle(step_id):
                    raise ValueError("Dependency graph has a cycle")

    def _topological_sort(self) -> list[set[str]]:
        """Sort into execution levels for parallelism.

        Steps in the same level have no deps on each other.

        Example:
            dependencies = {
                "b": ["a"],
                "c": ["a"],
                "d": ["b", "c"],
            }
            # Returns: [{"a"}, {"b", "c"}, {"d"}]
            # a runs first, then b and c in parallel, then d
        """
        levels: list[set[str]] = []
        remaining = set(self.steps.keys())

        while remaining:
            # Find steps with no unprocessed deps
            level = {
                step_id
                for step_id in remaining
                if all(
                    dep not in remaining
                    for dep in self.dependencies.get(step_id, [])
                )
            }

            if not level:
                raise ValueError("Cycle detected")

            levels.append(level)
            remaining -= level

        return levels

    async def execute(
        self,
        inputs: dict[str, Any],
        deps: DepsT,
        tracer: Tracer | None = None,
    ) -> ExecutionResult:
        """Execute pipeline."""
        result = ExecutionResult()

        for level in self._execution_levels:
            # Execute level in parallel
            tasks = []
            step_ids = []

            for step_id in level:
                step = self.steps[step_id]
                context = StepContext(
                    step_id=step_id,
                    inputs=inputs,
                    deps=deps,
                    step_outputs=result.outputs.copy(),
                    tracer=tracer,
                )
                tasks.append(self._execute_step(step_id, step, context, tracer))
                step_ids.append(step_id)

            outputs = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for step_id, output in zip(step_ids, outputs):
                if isinstance(output, Exception):
                    if isinstance(output, StepExecutionError):
                        raise output
                    raise StepExecutionError(step_id, output)

                result.outputs[step_id] = output

                # Collect usage
                step = self.steps[step_id]
                usage = self._extract_usage(step, output)
                if usage:
                    result.usages[step_id] = usage

                # Check early termination
                if isinstance(output, ConversationState):
                    if output.status == ConversationStatus.INCOMPLETE:
                        result.conversation_state = output
                        result.stopped_early = True
                        return result
                    result.conversation_state = output

        return result

    async def _execute_step(
        self,
        step_id: str,
        step: BaseStep,
        context: StepContext,
        tracer: Tracer | None,
    ) -> Any:
        """Execute single step with tracing."""
        if tracer:
            async with tracer.span(f"step.{step_id}"):
                return await step.execute(context)
        return await step.execute(context)

    def _extract_usage(self, step: BaseStep, output: Any) -> StepUsage | None:
        """Extract usage from step or output."""
        # AgentStep tracks usage
        if isinstance(step, AgentStep) and step.last_usage:
            return step.last_usage

        # Output might have usage
        if hasattr(output, "usage") and isinstance(output.usage, StepUsage):
            return output.usage

        # ChatResponse output
        from ..agent import ChatResponse
        if isinstance(output, ChatResponse):
            return StepUsage.from_chat_response(output)

        return None
```

### 7.6 Pipeline

```python
from __future__ import annotations
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ..tracing import Tracer, NoOpTracer
from .base import BaseStep, ConversationState
from .executor import PipelineExecutor
from .schemas import PipelineUsage

DepsT = TypeVar("DepsT")
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class PipelineResult(BaseModel, Generic[OutputT]):
    """Result from pipeline execution.

    Attributes:
        output: Final step's output, or None if stopped early.
        step_outputs: All step outputs by ID.
        conversation_state: ConversationState if a step returned one.
        usage: Aggregated usage metrics.
        stopped_early: True if stopped due to INCOMPLETE status.

    Example:
        result = await pipeline.execute(data, deps)

        if result.stopped_early:
            missing = result.conversation_state.context["missing"]
            return {"status": "incomplete", "missing": missing}

        print(f"Cost: ${result.usage.total_cost_dollars:.6f}")
        return {"status": "complete", "output": result.output}
    """

    output: OutputT | None = None
    step_outputs: dict[str, Any] = {}
    conversation_state: ConversationState | None = None
    usage: PipelineUsage | None = None
    stopped_early: bool = False

    model_config = {"arbitrary_types_allowed": True}


class Pipeline(Generic[DepsT, InputT, OutputT]):
    """Declarative DAG pipeline for multi-step AI workflows.

    Features:
    - Automatic parallelism from dependencies
    - Type-safe dependency access
    - Early termination on INCOMPLETE status
    - Aggregated usage tracking
    - Distributed tracing

    Example:
        pipeline = Pipeline(
            name="document_processor",
            steps={
                "extract": ExtractStep(),
                "classify": ClassifyStep(),
                "summarize": SummarizeStep(),
            },
            dependencies={
                "classify": ["extract"],
                "summarize": ["classify"],
            },
        )

        result = await pipeline.execute({"document": doc}, deps, tracer)
        summary = result.output

    Parallelism Example:
        dependencies = {
            "classify": ["extract"],
            "fetch_market": ["classify"],
            "fetch_user": ["classify"],  # Same dep as above
            "calculate": ["fetch_market", "fetch_user"],
        }
        # Execution:
        # Level 0: extract
        # Level 1: classify
        # Level 2: fetch_market, fetch_user (PARALLEL)
        # Level 3: calculate
    """

    def __init__(
        self,
        name: str,
        steps: dict[str, BaseStep[DepsT, Any]],
        dependencies: dict[str, list[str]] | None = None,
        output_step: str | None = None,
    ) -> None:
        """Initialize Pipeline.

        Args:
            name: Pipeline name (for tracing).
            steps: Dict of step_id -> step instance.
            dependencies: Dict of step_id -> [dependency_ids].
            output_step: Which step's output is the pipeline output.
                        Defaults to last step in topological order.

        Raises:
            ValueError: Invalid deps, unknown output_step, or cycles.
        """
        self.name = name
        self.steps = steps
        self.dependencies = dependencies or {}

        if output_step is not None and output_step not in steps:
            raise ValueError(f"output_step '{output_step}' not in steps")

        self._executor = PipelineExecutor(steps, self.dependencies)

        # Default output: last in topological order
        if output_step:
            self.output_step = output_step
        else:
            last_level = self._executor._execution_levels[-1]
            if len(last_level) > 1:
                raise ValueError(
                    f"Multiple terminal steps: {last_level}. "
                    f"Specify output_step explicitly."
                )
            self.output_step = next(iter(last_level))

    async def execute(
        self,
        input_data: InputT,
        deps: DepsT,
        tracer: Tracer | None = None,
    ) -> PipelineResult[OutputT]:
        """Execute the pipeline.

        Args:
            input_data: Input accessible via context.get_input().
            deps: Your deps accessible via context.deps.
            tracer: For distributed tracing.

        Returns:
            PipelineResult with output and usage.

        Raises:
            StepExecutionError: If any step fails.
        """
        effective_tracer = tracer or NoOpTracer()

        inputs = input_data if isinstance(input_data, dict) else {"data": input_data}

        async with effective_tracer.span(f"pipeline.{self.name}"):
            exec_result = await self._executor.execute(inputs, deps, effective_tracer)

        output = exec_result.outputs.get(self.output_step)
        usage = PipelineUsage.from_step_usages(exec_result.usages) if exec_result.usages else None

        return PipelineResult(
            output=output,
            step_outputs=exec_result.outputs,
            conversation_state=exec_result.conversation_state,
            usage=usage,
            stopped_early=exec_result.stopped_early,
        )
```

### 7.7 BasePipeline (Router)

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..tracing import Tracer
from .pipeline import Pipeline, PipelineResult

DepsT = TypeVar("DepsT")
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BasePipeline(ABC, Generic[DepsT, InputT, OutputT]):
    """Router between multiple pipelines.

    Implements Strategy pattern for pipeline selection.

    Use cases:
    - Simple vs complex paths
    - A/B testing
    - Fallback pipelines

    Example:
        class InvestmentRouter(BasePipeline[MyDeps, dict, Plan]):
            def __init__(self):
                super().__init__("investment_router")
                self.register_pipeline("simple", simple_pipeline)
                self.register_pipeline("complex", complex_pipeline)

            async def route(self, input_data: dict, deps: MyDeps) -> str:
                if input_data.get("amount", 0) < 10000:
                    return "simple"
                return "complex"

        router = InvestmentRouter()
        result = await router.execute({"amount": 50000}, deps)
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._pipelines: dict[str, Pipeline[DepsT, InputT, OutputT]] = {}

    def register_pipeline(
        self,
        name: str,
        pipeline: Pipeline[DepsT, InputT, OutputT],
    ) -> None:
        """Register a pipeline."""
        self._pipelines[name] = pipeline

    @abstractmethod
    async def route(self, input_data: InputT, deps: DepsT) -> str:
        """Determine which pipeline to execute. Return registered name."""
        ...

    async def execute(
        self,
        input_data: InputT,
        deps: DepsT,
        tracer: Tracer | None = None,
    ) -> PipelineResult[OutputT]:
        """Route and execute."""
        pipeline_name = await self.route(input_data, deps)

        if pipeline_name not in self._pipelines:
            raise ValueError(
                f"Unknown pipeline: '{pipeline_name}'. "
                f"Registered: {list(self._pipelines.keys())}"
            )

        return await self._pipelines[pipeline_name].execute(input_data, deps, tracer)
```

---

## 8. Core Module: Tools

### 8.1 The Problem Tools Solve

**Without @safe_tool:**

```python
async def web_search(query: str) -> str:
    # What happens when API is slow?
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com?q={query}")
        # Hangs for 60+ seconds if API is down
        return response.text

# What happens when API errors?
# Exception propagates, conversation crashes
# User sees: "Internal Server Error"
```

**With @safe_tool:**

```python
@safe_tool(timeout=10, max_retries=3)
async def web_search(query: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com?q={query}")
        return response.text

# Now:
# - Times out after 10 seconds per attempt
# - Retries up to 3 times with exponential backoff
# - On final failure: returns "Tool failed: ..." message
# - AI receives error message, responds gracefully
# - User sees: "I couldn't search the web right now, but I can help with..."
```

### 8.2 @safe_tool Decorator

```python
from __future__ import annotations
import asyncio
import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger("fastro_ai.tools")

DEFAULT_TOOL_TIMEOUT = 30
DEFAULT_TOOL_MAX_RETRIES = 3

P = ParamSpec("P")
R = TypeVar("R")


def safe_tool(
    timeout: int = DEFAULT_TOOL_TIMEOUT,
    max_retries: int = DEFAULT_TOOL_MAX_RETRIES,
    on_timeout: str | None = None,
    on_error: str | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R | str]]]:
    """Add timeout, retry, and error handling to AI tools.

    Args:
        timeout: Max seconds per attempt.
        max_retries: Max retry attempts.
        on_timeout: Custom timeout message.
        on_error: Custom error message. Use {error} for details.

    Example:
        @safe_tool(timeout=10, max_retries=2)
        async def web_search(query: str) -> str:
            '''Search the web.'''
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.com?q={query}")
                return response.text

        # Custom messages
        @safe_tool(
            timeout=30,
            on_timeout="Search took too long. Try simpler query.",
            on_error="Search unavailable: {error}",
        )
        async def search(query: str) -> str:
            ...
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R | str]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | str:
            last_error: Exception | None = None

            for attempt in range(max_retries):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"Tool '{func.__name__}' timeout attempt {attempt + 1}/{max_retries}"
                    )
                    last_error = asyncio.TimeoutError(f"Timeout after {timeout}s")
                except Exception as e:
                    logger.warning(
                        f"Tool '{func.__name__}' failed attempt {attempt + 1}/{max_retries}: {e}"
                    )
                    last_error = e

                # Exponential backoff
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt * 0.1)

            # All retries exhausted
            if isinstance(last_error, asyncio.TimeoutError):
                return on_timeout or f"Tool timed out after {max_retries} attempts"

            error_msg = str(last_error) if last_error else "Unknown error"
            if on_error:
                return on_error.format(error=error_msg)
            return f"Tool failed: {error_msg}"

        return wrapper

    return decorator
```

### 8.3 Toolset Classes

```python
from typing import Any, Callable

from pydantic_ai.toolsets import FunctionToolset


class FunctionToolsetBase(FunctionToolset):
    """Base class for organized tool sets.

    Example:
        @safe_tool(timeout=30)
        async def web_search(query: str) -> str:
            ...

        @safe_tool(timeout=10)
        async def get_weather(location: str) -> str:
            ...

        class WebToolset(FunctionToolsetBase):
            def __init__(self):
                super().__init__(
                    tools=[web_search, get_weather],
                    name="web",
                )

        agent = FastroAgent(toolsets=[WebToolset()])
    """

    def __init__(
        self,
        tools: list[Callable[..., Any]],
        name: str | None = None,
    ) -> None:
        super().__init__(tools=tools)
        self.name = name or self.__class__.__name__


class SafeToolset(FunctionToolsetBase):
    """Base for toolsets with only safe tools.

    Safe tools:
    - Don't access external networks
    - Don't modify system state
    - Have bounded execution time

    Example:
        class UtilityToolset(SafeToolset):
            def __init__(self):
                super().__init__(tools=[calculator, get_time], name="utils")
    """
    pass
```

---

## 9. Core Module: Usage

### 9.1 The Problem Usage Tracking Solves

**Without proper cost tracking:**

```python
# Floating point math is dangerous for billing
>>> 0.1 + 0.2
0.30000000000000004

>>> 0.000025 * 1000 + 0.0001 * 500
0.07500000000000001  # Should be exactly 0.075

# Over millions of transactions, errors compound
# Customer charged $1,000.00 vs $1,000.01
# Audit fails, lawsuits follow
```

**With microcents:**

```python
# Integer math is exact
>>> 250 + 1000  # 250 + 1000 microcents
1250

>>> 25 * 1000 + 100 * 500  # Per-1K pricing
75000  # Exactly 75,000 microcents = $0.075

# No precision errors, ever
```

### 9.2 Cost Calculator

```python
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger("fastro_ai.usage")

# Pricing in microcents per 1000 tokens
# 1 microcent = 1/10,000 cent = 1/1,000,000 dollar
DEFAULT_PRICING: dict[str, dict[str, int]] = {
    # OpenAI
    "gpt-4o": {
        "input_cost_per_1k_tokens": 250,      # $2.50/1M tokens
        "output_cost_per_1k_tokens": 1000,    # $10.00/1M tokens
    },
    "gpt-4o-mini": {
        "input_cost_per_1k_tokens": 15,       # $0.15/1M tokens
        "output_cost_per_1k_tokens": 60,      # $0.60/1M tokens
    },
    "gpt-4-turbo": {
        "input_cost_per_1k_tokens": 1000,
        "output_cost_per_1k_tokens": 3000,
    },

    # Anthropic
    "claude-3-5-sonnet": {
        "input_cost_per_1k_tokens": 300,
        "output_cost_per_1k_tokens": 1500,
    },
    "claude-3-5-sonnet-20241022": {
        "input_cost_per_1k_tokens": 300,
        "output_cost_per_1k_tokens": 1500,
    },
    "claude-3-opus": {
        "input_cost_per_1k_tokens": 1500,
        "output_cost_per_1k_tokens": 7500,
    },
    "claude-3-haiku": {
        "input_cost_per_1k_tokens": 25,
        "output_cost_per_1k_tokens": 125,
    },

    # Google
    "gemini-1.5-pro": {
        "input_cost_per_1k_tokens": 125,
        "output_cost_per_1k_tokens": 500,
    },
    "gemini-1.5-flash": {
        "input_cost_per_1k_tokens": 7,
        "output_cost_per_1k_tokens": 30,
    },
}


class CostCalculator:
    """Token cost calculator with microcents precision.

    Why microcents?
    - 1 microcent = 1/10,000 cent = 1/1,000,000 dollar
    - Integer math eliminates floating-point errors
    - Critical for billing accuracy

    Example:
        calc = CostCalculator()

        # Calculate cost
        cost = calc.calculate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
        # Input:  1000 * 250 / 1000 = 250 microcents
        # Output: 500 * 1000 / 1000 = 500 microcents
        # Total: 750 microcents = $0.00075

        print(f"Cost: {cost} microcents")
        print(f"Cost: ${calc.microcents_to_dollars(cost):.6f}")

        # Custom pricing
        my_pricing = DEFAULT_PRICING.copy()
        my_pricing["my-model"] = {
            "input_cost_per_1k_tokens": 500,
            "output_cost_per_1k_tokens": 1500,
        }
        calc = CostCalculator(pricing=my_pricing)
    """

    def __init__(self, pricing: dict[str, dict[str, int]] | None = None) -> None:
        """Initialize calculator.

        Args:
            pricing: Custom pricing dict. Defaults to DEFAULT_PRICING.
        """
        self.pricing = pricing if pricing is not None else DEFAULT_PRICING.copy()

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> int:
        """Calculate cost in microcents.

        Returns 0 for unknown models (logged as debug).
        """
        normalized = self._normalize_model_name(model)
        model_pricing = self.pricing.get(normalized)

        if not model_pricing:
            logger.debug(f"No pricing for '{model}' (normalized: '{normalized}')")
            return 0

        input_cost_per_1k = model_pricing.get("input_cost_per_1k_tokens", 0)
        output_cost_per_1k = model_pricing.get("output_cost_per_1k_tokens", 0)

        # Integer arithmetic for precision
        input_cost = (input_tokens * input_cost_per_1k) // 1000
        output_cost = (output_tokens * output_cost_per_1k) // 1000

        return input_cost + output_cost

    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name for lookup.

        Handles:
        - Provider prefix: "openai:gpt-4o" -> "gpt-4o"
        - Case: "GPT-4o" -> "gpt-4o"
        """
        if not model:
            return ""
        if ":" in model:
            model = model.split(":", 1)[1]
        return model.lower()

    def microcents_to_dollars(self, microcents: int) -> float:
        """Convert to dollars for display."""
        return microcents / 1_000_000

    def dollars_to_microcents(self, dollars: float) -> int:
        """Convert dollars to microcents."""
        return round(dollars * 1_000_000)

    def format_cost(self, microcents: int) -> dict[str, Any]:
        """Format cost in multiple representations."""
        return {
            "microcents": microcents,
            "cents": microcents // 10000,
            "dollars": self.microcents_to_dollars(microcents),
        }
```

---

## 10. Core Module: Tracing

### 10.1 The Problem Tracing Solves

**Without tracing:**

```python
# Something failed in production
# Logs show: "Error processing request"
# Which step? How long did each take? What was the input?
# Good luck debugging!
```

**With tracing:**

```python
tracer = SimpleTracer()
result = await pipeline.execute(data, deps, tracer=tracer)

# Logs show:
# [abc-123] Starting pipeline.investment_advisor
# [abc-124] Starting step.extract
# [abc-124] Completed step.extract in 0.234s
# [abc-125] Starting step.classify
# [abc-125] Completed step.classify in 0.567s
# [abc-126] Starting step.fetch_market
# [abc-127] Starting step.fetch_user      <- Parallel!
# [abc-127] Completed step.fetch_user in 0.890s
# [abc-126] Completed step.fetch_market in 1.234s
# [abc-128] Starting step.calculate
# [abc-128] FAILED step.calculate: ValueError: Invalid input
# [abc-123] FAILED pipeline.investment_advisor after 2.456s

# trace_id abc-123 correlates everything
# You know exactly where it failed and why
```

### 10.2 Tracer Protocol and Implementations

```python
from __future__ import annotations
import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Tracer(Protocol):
    """Protocol for distributed tracing.

    Implement for Logfire, OpenTelemetry, etc.

    Example (Logfire):
        import logfire

        class LogfireTracer:
            @asynccontextmanager
            async def span(self, name: str, **attrs) -> AsyncIterator[str]:
                trace_id = str(uuid.uuid4())
                with logfire.span(name, trace_id=trace_id, **attrs):
                    yield trace_id

            def log_metric(self, trace_id: str, name: str, value: Any) -> None:
                logfire.metric(name, value, trace_id=trace_id)

            def log_error(self, trace_id: str, error: Exception, ctx: dict | None = None) -> None:
                logfire.error(str(error), trace_id=trace_id, **(ctx or {}))
    """

    @asynccontextmanager
    async def span(self, name: str, **attributes: Any) -> AsyncIterator[str]:
        """Create traced span. Yields trace_id."""
        ...

    def log_metric(self, trace_id: str, name: str, value: Any) -> None:
        """Log metric."""
        ...

    def log_error(self, trace_id: str, error: Exception, context: dict[str, Any] | None = None) -> None:
        """Log error."""
        ...


class SimpleTracer:
    """Basic tracer using Python logging.

    Example:
        tracer = SimpleTracer()
        response = await agent.run("Hello", tracer=tracer)

        # Logs:
        # INFO [abc-123] Starting fastro_agent.run
        # INFO [abc-123] Completed fastro_agent.run in 1.234s
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("fastro_ai.tracing")

    @asynccontextmanager
    async def span(self, name: str, **attributes: Any) -> AsyncIterator[str]:
        trace_id = str(uuid.uuid4())
        start = time.perf_counter()

        self.logger.info(
            f"[{trace_id[:8]}] Starting {name}",
            extra={"trace_id": trace_id, "span": name, **attributes},
        )

        try:
            yield trace_id
        except Exception as e:
            duration = time.perf_counter() - start
            self.logger.error(
                f"[{trace_id[:8]}] FAILED {name} after {duration:.3f}s: {e}",
                exc_info=True,
            )
            raise
        finally:
            duration = time.perf_counter() - start
            self.logger.info(f"[{trace_id[:8]}] Completed {name} in {duration:.3f}s")

    def log_metric(self, trace_id: str, name: str, value: Any) -> None:
        self.logger.debug(f"[{trace_id[:8]}] Metric {name}={value}")

    def log_error(self, trace_id: str, error: Exception, context: dict[str, Any] | None = None) -> None:
        self.logger.error(f"[{trace_id[:8]}] Error: {error}", extra=context or {})


class NoOpTracer:
    """Tracer that does nothing. For disabled tracing or testing."""

    @asynccontextmanager
    async def span(self, name: str, **attributes: Any) -> AsyncIterator[str]:
        yield str(uuid.uuid4())

    def log_metric(self, trace_id: str, name: str, value: Any) -> None:
        pass

    def log_error(self, trace_id: str, error: Exception, context: dict[str, Any] | None = None) -> None:
        pass
```

---

## 11. Integration Patterns

### 11.1 Basic Agent Usage

```python
from fastro_ai import FastroAgent, SimpleTracer

# Create agent
agent = FastroAgent(
    model="openai:gpt-4o",
    system_prompt="You are a helpful assistant.",
)

# Simple call
response = await agent.run("What is the capital of France?")
print(response.content)       # "Paris"
print(response.cost_dollars)  # 0.000175

# With tracing
tracer = SimpleTracer()
response = await agent.run("Hello!", tracer=tracer)
```

### 11.2 Agent with Conversation History

```python
from fastro_ai import FastroAgent
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart

# Your memory service (you implement this)
class MyMemoryService:
    async def load(self, user_id: int) -> list:
        # Load from your database/Redis/etc.
        ...

    async def save(self, user_id: int, user_msg: str, assistant_msg: str):
        # Save to your storage
        ...

memory = MyMemoryService()
agent = FastroAgent()

async def chat(user_id: int, message: str) -> str:
    # Load history (YOUR responsibility)
    history_dicts = await memory.load(user_id)

    # Convert to PydanticAI format
    history = []
    for msg in history_dicts:
        if msg["role"] == "user":
            history.append(ModelRequest([UserPromptPart(msg["content"])]))
        else:
            history.append(ModelResponse([TextPart(msg["content"])]))

    # Run agent
    response = await agent.run(message, message_history=history)

    # Save (YOUR responsibility)
    await memory.save(user_id, message, response.content)

    return response.content
```

### 11.3 Agent with Tools

```python
from fastro_ai import FastroAgent, safe_tool, FunctionToolsetBase
import httpx

@safe_tool(timeout=30, max_retries=2)
async def web_search(query: str) -> str:
    """Search the web."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.example.com?q={query}")
        return r.text

@safe_tool(timeout=5)
async def calculator(expression: str) -> str:
    """Evaluate math expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

class MyToolset(FunctionToolsetBase):
    def __init__(self):
        super().__init__(tools=[web_search, calculator], name="my_tools")

agent = FastroAgent(
    system_prompt="You can search and calculate.",
    toolsets=[MyToolset()],
)

response = await agent.run("What is 15% of the Bitcoin price?")
print(response.tool_calls)  # [{"tool_name": "web_search", ...}, ...]
```

### 11.4 Simple Pipeline

```python
from pydantic import BaseModel
from fastro_ai import Pipeline, AgentStep, StepContext

class ExtractionResult(BaseModel):
    entities: list[str]
    summary: str

class Classification(BaseModel):
    category: str
    confidence: float

class ExtractStep(AgentStep[dict, ExtractionResult]):
    def __init__(self):
        super().__init__(system_prompt="Extract entities. Return JSON.")

    async def execute(self, context: StepContext[dict]) -> ExtractionResult:
        doc = context.get_input("document")
        response = await self.run_agent(context, f"Extract from: {doc}")
        return ExtractionResult.model_validate_json(response.content)

class ClassifyStep(AgentStep[dict, Classification]):
    def __init__(self):
        super().__init__(system_prompt="Classify content. Return JSON.")

    async def execute(self, context: StepContext[dict]) -> Classification:
        extraction = context.get_dependency("extract", ExtractionResult)
        response = await self.run_agent(context, f"Classify: {extraction.summary}")
        return Classification.model_validate_json(response.content)

pipeline = Pipeline(
    name="document_processor",
    steps={"extract": ExtractStep(), "classify": ClassifyStep()},
    dependencies={"classify": ["extract"]},
)

result = await pipeline.execute({"document": "..."}, {})
print(result.output.category)
print(result.usage.total_cost_dollars)
```

### 11.5 Pipeline with Parallelism

```python
pipeline = Pipeline(
    name="investment_advisor",
    steps={
        "analyze": AnalyzeStep(),
        "fetch_market": FetchMarketStep(),  # These run
        "fetch_user": FetchUserStep(),       # in PARALLEL!
        "calculate": CalculateStep(),
    },
    dependencies={
        "fetch_market": ["analyze"],
        "fetch_user": ["analyze"],
        "calculate": ["fetch_market", "fetch_user"],
    },
)

# Execution:
# Level 0: analyze
# Level 1: fetch_market, fetch_user (PARALLEL - saves time!)
# Level 2: calculate
```

### 11.6 Multi-Turn Conversation

```python
from fastro_ai import Pipeline, AgentStep, ConversationState, ConversationStatus

class InvestmentInfo(BaseModel):
    amount: float | None = None
    risk: str | None = None
    horizon: int | None = None

    def is_complete(self) -> bool:
        return all([self.amount, self.risk, self.horizon])

    def missing_fields(self) -> list[str]:
        missing = []
        if not self.amount: missing.append("amount")
        if not self.risk: missing.append("risk tolerance")
        if not self.horizon: missing.append("time horizon")
        return missing

class GatherInfoStep(AgentStep[MyDeps, ConversationState[InvestmentInfo]]):
    async def execute(self, context) -> ConversationState[InvestmentInfo]:
        msg = context.get_input("message")
        response = await self.run_agent(context, f"Extract investment params: {msg}")
        info = InvestmentInfo.model_validate_json(response.content)

        if info.is_complete():
            return ConversationState(status=ConversationStatus.COMPLETE, data=info)

        return ConversationState(
            status=ConversationStatus.INCOMPLETE,
            data=info,
            context={"missing": info.missing_fields()},
        )

class CalculateStep(AgentStep[MyDeps, InvestmentPlan]):
    async def execute(self, context) -> InvestmentPlan:
        # Only runs when GatherInfoStep returns COMPLETE
        info = context.get_dependency("gather").data
        response = await self.run_agent(context, f"Create plan: {info}")
        return InvestmentPlan.model_validate_json(response.content)

pipeline = Pipeline(
    steps={"gather": GatherInfoStep(), "calculate": CalculateStep()},
    dependencies={"calculate": ["gather"]},
)

# Turn 1
result = await pipeline.execute({"message": "I want to invest"}, deps)
if result.stopped_early:
    print(f"Need: {result.conversation_state.context['missing']}")
    # User provides more info...

# Turn 2
result = await pipeline.execute({"message": "50k, medium, 10 years"}, deps)
if not result.stopped_early:
    print(result.output)  # InvestmentPlan
```

### 11.7 FastAPI Integration

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastro_ai import FastroAgent, Pipeline, SimpleTracer

app = FastAPI()

# Shared instances
agent = FastroAgent(system_prompt="You are helpful.")
pipeline = Pipeline(name="my_pipeline", steps={...}, dependencies={...})

def get_tracer() -> SimpleTracer:
    return SimpleTracer()

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

@app.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    tracer: SimpleTracer = Depends(get_tracer),
):
    # Load history (your service)
    history = await memory_service.load(request.conversation_id, db)

    # Run agent
    response = await agent.run(
        request.message,
        message_history=history,
        tracer=tracer,
    )

    # Store (your service)
    await memory_service.store(request.conversation_id, request.message, response.content, db)

    # Track usage (your service)
    await usage_service.record(request.conversation_id, response.cost_microcents, db)

    return {"content": response.content, "cost": response.cost_microcents}
```

---

## 12. Error Handling

### 12.1 Exception Types

```python
class FastroAIError(Exception):
    """Base exception."""
    pass

class StepExecutionError(FastroAIError):
    """Pipeline step failed."""

    def __init__(self, step_id: str, original_error: Exception):
        self.step_id = step_id
        self.original_error = original_error
        super().__init__(f"Step '{step_id}' failed: {original_error}")

class PipelineValidationError(FastroAIError):
    """Invalid pipeline configuration."""
    pass
```

### 12.2 Handling Errors

```python
from fastro_ai.pipelines import StepExecutionError

try:
    result = await pipeline.execute(data, deps, tracer)
except StepExecutionError as e:
    print(f"Step '{e.step_id}' failed: {e.original_error}")

    if e.step_id == "fetch_external":
        return fallback_response()
    raise
```

---

## 13. Package Structure

```
fastro_ai/
├── __init__.py              # Public exports
├── py.typed                 # PEP 561 marker
│
├── agent/
│   ├── __init__.py
│   ├── agent.py             # FastroAgent
│   └── schemas.py           # AgentConfig, ChatResponse, StreamChunk
│
├── pipelines/
│   ├── __init__.py
│   ├── base.py              # BaseStep, StepContext, ConversationState
│   ├── agent_step.py        # AgentStep
│   ├── executor.py          # PipelineExecutor
│   ├── pipeline.py          # Pipeline, PipelineResult
│   ├── router.py            # BasePipeline
│   └── schemas.py           # StepUsage, PipelineUsage
│
├── tools/
│   ├── __init__.py
│   ├── decorators.py        # @safe_tool
│   └── toolsets.py          # FunctionToolsetBase, SafeToolset
│
├── usage/
│   ├── __init__.py
│   └── calculator.py        # CostCalculator, DEFAULT_PRICING
│
└── tracing/
    ├── __init__.py
    └── tracer.py            # Tracer, SimpleTracer, NoOpTracer
```

**Estimated Lines:**

| Module | Lines |
|--------|-------|
| agent/ | ~320 |
| pipelines/ | ~590 |
| tools/ | ~130 |
| usage/ | ~150 |
| tracing/ | ~150 |
| **Total** | **~1,340** |

---

## 14. Public API Surface

```python
"""FastroAI - Lightweight AI orchestration built on PydanticAI."""

from .agent import FastroAgent, AgentConfig, ChatResponse, StreamChunk
from .pipelines import (
    Pipeline, PipelineResult,
    BaseStep, AgentStep, StepContext,
    ConversationState, ConversationStatus,
    BasePipeline,
    StepUsage, PipelineUsage,
)
from .tools import safe_tool, FunctionToolsetBase, SafeToolset
from .usage import CostCalculator, DEFAULT_PRICING
from .tracing import Tracer, SimpleTracer, NoOpTracer

__version__ = "1.0.0"

__all__ = [
    # Agent
    "FastroAgent", "AgentConfig", "ChatResponse", "StreamChunk",

    # Pipelines
    "Pipeline", "PipelineResult",
    "BaseStep", "AgentStep", "StepContext",
    "ConversationState", "ConversationStatus",
    "BasePipeline",
    "StepUsage", "PipelineUsage",

    # Tools
    "safe_tool", "FunctionToolsetBase", "SafeToolset",

    # Usage
    "CostCalculator", "DEFAULT_PRICING",

    # Tracing
    "Tracer", "SimpleTracer", "NoOpTracer",
]
```

---

## 15. Implementation Plan

### Phase 1: Core Agent (Week 1)
- `agent/` module
- `usage/calculator.py`
- `tracing/` module
- Unit tests

### Phase 2: Tools (Week 1)
- `tools/` module
- `@safe_tool` decorator
- Integration tests

### Phase 3: Pipelines (Week 2)
- `pipelines/` module
- Executor with parallelism
- ConversationState handling
- Integration tests

### Phase 4: Polish (Week 2)
- `BasePipeline` router
- Documentation
- Package configuration

### Phase 5: Release (Week 3)
- PyPI publish
- GitHub CI/CD
- API reference docs

---

## 16. Appendices

### 16.1 Dependencies

```toml
[project]
name = "fastro-ai"
version = "1.0.0"
description = "Lightweight AI orchestration built on PydanticAI"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "pydantic-ai>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "mypy>=1.8",
    "ruff>=0.2",
]
logfire = ["logfire>=1.0"]
```

### 16.2 Why These Design Choices?

| Choice | Why |
|--------|-----|
| **Microcents** | Floating-point precision errors compound in billing |
| **Tracer protocol** | Let apps integrate their own observability |
| **No memory persistence** | Storage is app domain, framework stays agnostic |
| **Generic DepsT** | Apps define their own dependency types |
| **ConversationState** | Clear signal for multi-turn pause/resume |
| **@safe_tool** | Tools shouldn't crash conversations |
| **Topological levels** | Enable automatic parallelism |

### 16.3 What FastroAI Is NOT

- ❌ A database ORM
- ❌ A web framework
- ❌ A billing system
- ❌ A memory/RAG system
- ❌ A competitor to PydanticAI (it's built ON PydanticAI)

FastroAI is orchestration primitives. Your app provides everything else.

---

**End of Specification**
