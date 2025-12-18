# FastroAI Implementation Journal

This document tracks the implementation progress of FastroAI's orchestration layer enhancements. Updated as we build.

---

## Rationale

### Why This Work?

FastroAI started as a PydanticAI wrapper adding production concerns (cost tracking, tracing, safe tools). The current implementation works well for **single agent calls** and **simple pipelines**, but lacks:

1. **Usage tracking at step level for multi-agent steps** - `as_step()` tracks usage, but custom steps with multiple `agent.run()` calls don't aggregate automatically
2. **Configuration inheritance** - No way to set defaults at pipeline level that flow down to steps and agent calls
3. **`ctx.run()` integration point** - Steps with multiple agents require manual tracer passing and no automatic usage capture
4. **Step decorator** - Only class-based steps and `as_step()` exist; no concise decorator for custom logic
5. **Structured error hierarchy** - `StepExecutionError` exists but no base class or validation-specific errors

### The Goal

Extend the "goodies" from agent → step → pipeline:
- Usage bubbles up automatically (even for multi-agent steps)
- Config cascades down with overrides
- Tracing flows through without manual passing
- Three step patterns for progressive disclosure

---

## Philosophical Analysis: Current vs Proposed

### Current Philosophy (Two Patterns)

**Pattern 1: `as_step()` - Agent IS the step**

The simplest case. The step is just a wrapper around a single agent call.

```python
# From agent/agent.py - AgentStepWrapper (CURRENT - will be simplified)
agent = FastroAgent(model="gpt-4o", system_prompt="...")
step = agent.as_step(lambda ctx: f"Process: {ctx.get_input('text')}")

# CURRENT AgentStepWrapper.execute() - manual forwarding:
async def execute(self, context: StepContext[DepsT]) -> OutputT:
    message = self._prompt(context)
    response = await self._agent.run(
        message=message,
        deps=context.deps,
        tracer=context.tracer,
    )
    self._last_usage = StepUsage.from_chat_response(response)
    return response.output

# AFTER Phase 1 - uses ctx.run():
async def execute(self, context: StepContext[DepsT]) -> OutputT:
    message = self._prompt(context)
    response = await context.run(self._agent, message)  # Simple!
    return response.output
```

After Phase 1, `AgentStepWrapper` will use `ctx.run()` like everything else.

**Pattern 2: Custom `BaseStep` - Step OWNS agents, calls directly**

For complex steps with logic, conditions, or multiple agents.

```python
class ResearchStep(BaseStep[MyDeps, Report]):
    def __init__(self):
        self.classifier = FastroAgent(model="gpt-4o-mini", ...)
        self.writer = FastroAgent(model="gpt-4o", ...)

    async def execute(self, context: StepContext[MyDeps]) -> Report:
        # Step owns agents, calls them DIRECTLY
        cat_response = await self.classifier.run(
            f"Classify: {context.get_input('topic')}",
            deps=context.deps,       # MANUAL forwarding
            tracer=context.tracer,   # MANUAL forwarding
        )

        write_response = await self.writer.run(
            f"Write about: {cat_response.output}",
            deps=context.deps,       # MANUAL again
            tracer=context.tracer,   # MANUAL again
        )

        return Report(...)
        # Usage? NOT automatically tracked. Executor won't find it.
```

**Problems with Pattern 2:**
1. Manual `deps=context.deps, tracer=context.tracer` on every call - verbose, error-prone
2. No automatic usage aggregation across multiple agent calls
3. No way for executor to know what usage occurred inside the step

### Proposed Philosophy: `ctx.run()` - Context MEDIATES

Instead of steps calling agents directly, steps call agents THROUGH the context.

```python
class ResearchStep(BaseStep[MyDeps, Report]):
    classifier = FastroAgent(model="gpt-4o-mini", ...)
    writer = FastroAgent(model="gpt-4o", ...)

    async def execute(self, ctx: StepContext[MyDeps]) -> Report:
        # Context mediates ALL agent calls
        cat_response = await ctx.run(self.classifier, f"Classify: {ctx.get_input('topic')}")
        # ^ tracer passed automatically, usage recorded in ctx.usage

        write_response = await ctx.run(self.writer, f"Write about: {cat_response.output}")
        # ^ usage ACCUMULATED into ctx.usage (cat + write)

        return Report(...)
        # ctx.usage now contains TOTAL usage from both calls
```

**What `ctx.run()` provides:**
1. **Automatic tracer passing** - no more `tracer=context.tracer`
2. **Automatic deps passing** - no more `deps=context.deps`
3. **Usage accumulation** - `ctx.usage` sums all calls automatically
4. **Future: config inheritance** - timeout, retries from step/pipeline config
5. **Future: budget enforcement** - check budget before each call

### This is a FUNDAMENTAL Architectural Change

| Aspect | Current (Pattern 2) | Proposed (`ctx.run()`) |
|--------|---------------------|------------------------|
| Who calls agent? | Step calls `agent.run()` directly | Step calls `ctx.run(agent, msg)` |
| deps/tracer | Manual forwarding each call | Automatic via context |
| Usage tracking | Convention-based, unreliable | Automatic accumulation |
| Context role | Data bag (inputs, deps, outputs) | Integration point (mediator) |
| Config inheritance | Not possible | Central enforcement point |

### Clean Slate Approach

Since FastroAI hasn't launched yet, we take the cleanest approach:
- `ctx.run()` is THE way to call agents from steps
- `as_step()` will be updated to use `ctx.run()` internally
- No fallback patterns needed - just `ctx.usage`
- Simpler, more consistent codebase

---

## Current State (Verified from Codebase)

### What's Complete

| Component | Location | Notes |
|-----------|----------|-------|
| `FastroAgent` | `agent/agent.py` | run(), run_stream(), cost tracking, tracing, output_type |
| `agent.as_step()` | `agent/agent.py:442-478` | Returns `AgentStepWrapper` (will use ctx.run() after Phase 1) |
| `AgentStepWrapper` | `agent/agent.py:481-523` | Currently manual; will use ctx.run() after Phase 1 |
| `StepContext` | `pipelines/base.py:68-163` | step_id, deps, tracer, get_input(), get_dependency() |
| `BaseStep` | `pipelines/base.py:166-192` | Abstract base with execute() method |
| `ConversationState/Status` | `pipelines/base.py:25-65` | Multi-turn signaling, COMPLETE/INCOMPLETE |
| `Pipeline` | `pipelines/pipeline.py` | name, steps, dependencies, output_step, execute() |
| `PipelineExecutor` | `pipelines/executor.py` | Topological sort, parallelism, early termination |
| `StepUsage` | `pipelines/schemas.py:17-64` | from_chat_response(), __add__() for aggregation |
| `PipelineUsage` | `pipelines/schemas.py:67-101` | from_step_usages(), total_cost_dollars |
| `StepExecutionError` | `pipelines/executor.py:21-27` | Has step_id, original_error (inherits Exception) |
| `BasePipeline` (Router) | `pipelines/router.py` | register_pipeline(), route(), execute() - FULLY IMPLEMENTED |
| `@safe_tool` | `tools/decorators.py` | Timeout, retry, graceful errors |
| `Tracer` protocol | `tracing/tracer.py` | SimpleTracer, NoOpTracer |
| `CostCalculator` | `usage/calculator.py` | Microcents precision, DEFAULT_PRICING |

### What's Missing

| Component | Priority | Notes |
|-----------|----------|-------|
| `ctx.run(agent, msg)` | HIGH | Key integration point for multi-agent steps |
| `ctx.usage` property | HIGH | Accumulator for usage within a step |
| `ctx.config` property | MEDIUM | Merged config for the step |
| `StepConfig` class | MEDIUM | timeout, retries, retry_delay, cost_budget |
| `PipelineConfig` class | MEDIUM | Extends StepConfig + trace, on_error |
| Pipeline config params | MEDIUM | `config=`, `step_configs=` in constructor |
| Config inheritance logic | MEDIUM | Pipeline → Step → per-call resolution |
| `@step` decorator | MEDIUM | Concise alternative to class-based steps |
| `FastroAIError` base | LOW | Base exception class |
| `PipelineValidationError` | LOW | Currently uses ValueError |
| `CostBudgetExceeded` | LOW | For budget enforcement |

### Usage Extraction (Current → New)

**Current** (from `executor.py:186-199`) - convention-based with fallbacks:
```python
def _extract_usage(self, step, output):
    # Multiple fallback patterns...
    if hasattr(step, "last_usage"): ...
    if hasattr(output, "usage"): ...
    if isinstance(output, ChatResponse): ...
```

**After Phase 1** - simple, single path:
```python
def _extract_usage(self, context: StepContext) -> StepUsage | None:
    if context.usage.cost_microcents > 0 or context.usage.input_tokens > 0:
        return context.usage
    return None
```

All steps use `ctx.run()`, so usage is always in `ctx.usage`. No fallbacks needed.

---

## Implementation Plan

### Implementation Strategy: Incremental Core-First

**Key insight**: `ctx.run()` is the CORE architectural change. Everything else builds on it.

**Strategy**: Implement minimal `ctx.run()` FIRST, then layer on config/budget/errors.

| Phase | Focus | Depends On |
|-------|-------|------------|
| 1 | **Minimal `ctx.run()`** - tracer + usage only | Nothing |
| 2 | Config classes (`StepConfig`, `PipelineConfig`) | Nothing |
| 3 | Enhanced `ctx.run()` with config | Phase 1, 2, 6 |
| 4 | Pipeline config integration | Phase 2, 3 |
| 5 | `@step` decorator | Phase 1 |
| 6 | Error hierarchy | Nothing (can parallel with 1, 2) |
| 7 | Polish & docs | All above |

---

### Phase 1: Minimal `ctx.run()` (CORE CHANGE)

**Goal**: Implement the fundamental pattern shift - context as mediator.

**What we're adding**:
```python
class StepContext:
    # Existing: step_id, deps, tracer, get_input(), get_dependency()

    # NEW:
    _usage: StepUsage  # Accumulator, starts at zero

    @property
    def usage(self) -> StepUsage:
        """Accumulated usage from all ctx.run() calls."""
        return self._usage

    async def run(
        self,
        agent: FastroAgent[OutputT],
        message: str,
    ) -> ChatResponse[OutputT]:
        """Run agent with automatic tracer and usage tracking.

        This is the MINIMAL version - no config, no timeout, no budget.
        Just the core pattern: tracer forwarding + usage accumulation.
        """
        response = await agent.run(
            message,
            deps=self._deps,
            tracer=self._tracer,
        )
        self._usage = self._usage + StepUsage.from_chat_response(response)
        return response
```

**Why minimal first?**
- Validates the core pattern before adding complexity
- Easier to test and debug
- Config/timeout/budget can be added incrementally later

#### Step 1.1: Add `_usage` to StepContext

Modify `fastroai/pipelines/base.py`:
- Add `_usage: StepUsage` initialized to zero in `__init__`
- Add `usage` property

#### Step 1.2: Implement minimal `ctx.run()`

Add to `StepContext`:
```python
async def run(
    self,
    agent: FastroAgent[OutputT],
    message: str,
) -> ChatResponse[OutputT]:
    response = await agent.run(message, deps=self._deps, tracer=self._tracer)
    self._usage = self._usage + StepUsage.from_chat_response(response)
    return response
```

#### Step 1.3: Update executor to use `ctx.usage`

Simplify `_extract_usage` in `executor.py` - just use context:
```python
def _extract_usage(self, context: StepContext) -> StepUsage | None:
    """Extract usage from context. Simple - no fallbacks needed."""
    if context.usage.cost_microcents > 0 or context.usage.input_tokens > 0:
        return context.usage
    return None
```

#### Step 1.4: Update AgentStepWrapper to use `ctx.run()`

Modify `AgentStepWrapper.execute()` in `agent/agent.py`:
```python
async def execute(self, context: StepContext[DepsT]) -> OutputT:
    message = self._prompt if isinstance(self._prompt, str) else self._prompt(context)
    response = await context.run(self._agent, message)
    return response.output
```

No more `self._last_usage` - usage is tracked via `ctx.usage`.

**Files to modify**:
- `fastroai/pipelines/base.py` (StepContext)
- `fastroai/pipelines/executor.py` (_extract_usage simplified)
- `fastroai/agent/agent.py` (AgentStepWrapper)

**Tests**:
- `ctx.run()` passes tracer automatically
- `ctx.run()` passes deps automatically
- `ctx.usage` accumulates across multiple calls
- `AgentStepWrapper` uses `ctx.run()` internally

---

### Phase 2: Configuration Classes

**Goal**: Create config dataclasses (can run in parallel with Phase 1).

#### Step 2.1: Create Config Module

Create `fastroai/pipelines/config.py`:

```python
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class StepConfig:
    """Configuration for a pipeline step."""
    timeout: float | None = None
    retries: int = 0
    retry_delay: float = 1.0
    cost_budget: int | None = None  # In microcents


@dataclass
class PipelineConfig(StepConfig):
    """Configuration for a pipeline with additional options."""
    trace: bool = True
    on_error: Literal["fail", "continue"] = "fail"
```

**Files to modify**:
- Create `fastroai/pipelines/config.py`
- Update `fastroai/pipelines/__init__.py` exports
- Update `fastroai/__init__.py` exports

**Tests**:
- Default values
- Inheritance (PipelineConfig has StepConfig fields)

---

### Phase 3: Enhanced `ctx.run()` with Config

**Goal**: Add config awareness to `ctx.run()` - timeout, retries, budget.

**Depends on**: Phase 1 (minimal ctx.run), Phase 2 (config classes), Phase 6 (for `CostBudgetExceeded`)

#### Step 3.1: Add `config` to StepContext

Modify `StepContext.__init__` to accept:
- `config: StepConfig | None = None` - merged config for this step

Add property:
- `config` - returns step config (or default StepConfig if None)

#### Step 3.2: Enhance `ctx.run()` with config

```python
async def run(
    self,
    agent: FastroAgent[OutputT],
    message: str,
    timeout: float | None = None,  # Per-call override
    retries: int | None = None,    # Per-call override
) -> ChatResponse[OutputT]:
    """Run agent with config inheritance and usage tracking."""

    # Check budget BEFORE call
    if self.config.cost_budget and self._usage.cost_microcents >= self.config.cost_budget:
        raise CostBudgetExceeded(
            self.config.cost_budget,
            self._usage.cost_microcents,
            self._step_id
        )

    # Resolve effective config (per-call overrides step config)
    effective_timeout = timeout if timeout is not None else self.config.timeout
    effective_retries = retries if retries is not None else self.config.retries

    # Execute with timeout/retry wrapper
    response = await self._execute_with_config(
        agent, message, effective_timeout, effective_retries
    )

    # Accumulate usage
    self._usage = self._usage + StepUsage.from_chat_response(response)
    return response
```

#### Step 3.3: Implement `_execute_with_config`

```python
async def _execute_with_config(
    self,
    agent: FastroAgent[OutputT],
    message: str,
    timeout: float | None,
    retries: int,
) -> ChatResponse[OutputT]:
    """Execute with timeout and retry logic."""
    import asyncio

    last_error: Exception | None = None
    retry_delay = self.config.retry_delay if self.config else 1.0

    for attempt in range(max(1, retries + 1)):
        try:
            coro = agent.run(message, deps=self._deps, tracer=self._tracer)
            if timeout:
                return await asyncio.wait_for(coro, timeout=timeout)
            return await coro
        except asyncio.TimeoutError:
            last_error = asyncio.TimeoutError(f"Timed out after {timeout}s")
        except Exception as e:
            last_error = e

        if attempt < retries:
            await asyncio.sleep(retry_delay * (2 ** attempt))

    raise last_error or RuntimeError("Unexpected error")
```

**Files to modify**:
- `fastroai/pipelines/base.py`

**Tests**:
- Timeout causes retry
- Retries with exponential backoff
- Budget exceeded raises CostBudgetExceeded
- Per-call overrides work

---

### Phase 4: Pipeline Config Integration

**Goal**: Pipeline accepts config params and passes merged config to steps.

#### Step 4.1: Pipeline Constructor Updates

Add to Pipeline.__init__:
- `config: PipelineConfig | None = None`
- `step_configs: dict[str, StepConfig] | None = None`

**Files to modify**:
- `fastroai/pipelines/pipeline.py`

#### Step 4.2: Config Resolution in Executor

Implement config merging:
1. Start with `PipelineConfig` defaults
2. Merge step's own config (if class has `config` attribute)
3. Override with `step_configs[step_id]` if present

Pass merged config to `StepContext`.

**Files to modify**:
- `fastroai/pipelines/executor.py`
- `fastroai/pipelines/pipeline.py`

**Tests**:
- Pipeline defaults apply to all steps
- Step class config overrides pipeline
- step_configs overrides step's own config
- Per-call overrides via ctx.run() work

---

### Phase 5: @step Decorator

**Goal**: Concise alternative to class-based steps.

#### Step 5.1: Implement Decorator

```python
def step(
    func: Callable | None = None,
    *,
    timeout: float | None = None,
    retries: int = 0,
    retry_delay: float = 1.0,
    cost_budget: int | None = None,
) -> BaseStep | Callable[[Callable], BaseStep]:
    """Decorator to create a step from a function."""

    def decorator(fn: Callable) -> BaseStep:
        config = StepConfig(
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
            cost_budget=cost_budget,
        )
        return _FunctionStep(fn, config)

    if func is not None:
        return decorator(func)
    return decorator


class _FunctionStep(BaseStep[Any, Any]):
    """Internal step class wrapping a function."""

    def __init__(self, func: Callable, config: StepConfig):
        self._func = func
        self.config = config

    async def execute(self, context: StepContext[Any]) -> Any:
        if asyncio.iscoroutinefunction(self._func):
            return await self._func(context)
        return self._func(context)
```

**Files to modify**:
- Create `fastroai/pipelines/decorators.py`
- Update `fastroai/pipelines/__init__.py`
- Update `fastroai/__init__.py`

**Tests**:
- Sync and async functions
- With and without config params
- Works alongside class-based steps in same Pipeline
- Config from decorator is used

---

### Phase 6: Error Hierarchy

**Goal**: Create structured exception classes for clear error handling.

**Note**: This phase can run in parallel with Phases 1-2. However, `CostBudgetExceeded` is needed for Phase 3's budget checking feature.

#### Step 6.1: Create Error Module

Create `fastroai/errors.py`:

```python
class FastroAIError(Exception):
    """Base exception for all FastroAI errors."""
    pass


class PipelineValidationError(FastroAIError):
    """Invalid pipeline configuration.

    Raised at pipeline construction time for:
    - Unknown step in dependencies
    - Circular dependencies
    - Missing output_step when needed
    """
    pass


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

#### Step 6.2: Update StepExecutionError

Modify `fastroai/pipelines/executor.py` to make `StepExecutionError` inherit from `FastroAIError`:

```python
from ..errors import FastroAIError

class StepExecutionError(FastroAIError):
    """A pipeline step failed during execution."""
    # ... rest unchanged
```

#### Step 6.3: Update Pipeline Validation

Modify `fastroai/pipelines/executor.py` `_validate()` to raise `PipelineValidationError` instead of `ValueError`:

```python
from ..errors import PipelineValidationError

def _validate(self) -> None:
    # ... existing logic, but raise PipelineValidationError instead of ValueError
```

**Files to modify**:
- Create `fastroai/errors.py`
- `fastroai/pipelines/executor.py` (import and use new errors)
- `fastroai/__init__.py` (export errors)

**Tests**:
- `FastroAIError` is base class for all errors
- `StepExecutionError` inherits from `FastroAIError`
- `PipelineValidationError` raised for invalid config
- `CostBudgetExceeded` has correct attributes

---

### Phase 7: Polish & Documentation

#### Step 7.1: Update Exports

Ensure all new types exported from `fastroai`:
- `StepConfig`, `PipelineConfig`
- `FastroAIError`, `PipelineValidationError`, `CostBudgetExceeded`
- `step` decorator

#### Step 7.2: Update CLAUDE.md

Add new patterns and APIs.

#### Step 7.3: Comprehensive Tests

- Integration tests for full pipeline with new features
- Edge cases (empty steps, no agent calls, budget exceeded mid-step)

---

## Decisions Log

### Decision 1: `ctx.run()` vs `AgentStep.run_agent()`

**Date**: 2024-12-15

**Context**: Implementation spec had `AgentStep` with `run_agent(context, msg)` where agent is bound to step class.

**Decision**: Use `ctx.run(agent, msg)` instead.

**Rationale**:
- More flexible - agent passed as parameter, not bound to step
- Better for multi-agent steps with different agents
- Single integration point in context
- Cleaner: `ctx.run(classifier, msg)` vs `self.run_agent(ctx, msg)`

### Decision 2: Separate dependencies dict

**Date**: 2024-12-15

**Decision**: Keep separate `dependencies` dict in Pipeline.

**Rationale**:
- Explicit parallelism - you see what can run concurrently
- No magic inference of data flow
- Matches current implementation

### Decision 3: Three step patterns coexist

**Date**: 2024-12-15

**Decision**: Support `as_step()`, `@step`, and `class BaseStep`.

**Rationale**:
- Progressive disclosure
- `as_step()` for single-agent, prompt-only
- `@step` for concise multi-agent or logic
- `class` for explicit typing and complex initialization

### Decision 4: Config inheritance order

**Date**: 2024-12-15

**Decision**: Pipeline defaults → Step config → step_configs override → per-call override

**Rationale**: Most specific wins.

### Decision 5: Budget check timing

**Date**: 2024-12-15

**Decision**: Check budget BEFORE each `ctx.run()` call, not after.

**Rationale**: Prevents spending over budget. Current call completes, next call blocked.

---

## Notes

### Note 1: Clean Implementation

Since this is pre-launch, we implement the cleanest approach:
- All steps use `ctx.run()` for agent calls
- `as_step()` updated to use `ctx.run()` internally
- Single usage extraction path via `ctx.usage`
- Pipelines without config get default config

### Note 2: StepUsage Accumulation

```python
async def execute(self, ctx):
    r1 = await ctx.run(agent1, "msg1")  # ctx.usage = r1.usage
    r2 = await ctx.run(agent2, "msg2")  # ctx.usage = r1.usage + r2.usage
    return result
```

### Note 3: BasePipeline Router

Already fully implemented in `router.py`. No work needed.

---

## Progress Tracker

| Phase | Step | Status | Date | Notes |
|-------|------|--------|------|-------|
| 1 | 1.1 Add _usage to StepContext | ✅ Done | 2025-12-16 | Added _usage property |
| 1 | 1.2 Implement minimal ctx.run() | ✅ Done | 2025-12-16 | tracer + deps + usage |
| 1 | 1.3 Simplify executor usage extraction | ✅ Done | 2025-12-16 | Just use ctx.usage |
| 1 | 1.4 Update AgentStepWrapper | ✅ Done | 2025-12-16 | Uses ctx.run() now |
| 2 | 2.1 Create Config Module | ✅ Done | 2025-12-16 | StepConfig, PipelineConfig |
| 3 | 3.1 Add config to StepContext | ✅ Done | 2025-12-16 | config property added |
| 3 | 3.2 Enhance ctx.run() with config | ✅ Done | 2025-12-16 | timeout, retries, budget |
| 3 | 3.3 Implement _execute_with_config | ✅ Done | 2025-12-16 | retry logic with backoff |
| 4 | 4.1 Pipeline config params | ✅ Done | 2025-12-16 | config=, step_configs= |
| 4 | 4.2 Config resolution in executor | ✅ Done | 2025-12-16 | _resolve_config(), _merge_configs() |
| 5 | 5.1 @step Decorator | ✅ Done | 2025-12-16 | decorators.py created |
| 6 | 6.1 Create error module | ✅ Done | 2025-12-16 | FastroAIError, CostBudgetExceededError |
| 6 | 6.2 Update StepExecutionError | ✅ Done | 2025-12-16 | Inherits FastroAIError |
| 6 | 6.3 Update validation errors | ✅ Done | 2025-12-16 | PipelineValidationError |
| 7 | 7.1 Update Exports | ✅ Done | 2025-12-16 | fastroai/__init__.py updated |
| 7 | 7.2 Update CLAUDE.md | ✅ Done | 2025-12-16 | New patterns documented |
| 7 | 7.3 Comprehensive Tests | ✅ Done | 2025-12-16 | 98% coverage |

---

## Open Questions

1. **Retry scope**: Step-level retries (retry whole step) vs call-level (retry individual ctx.run())?
   - Current decision: ctx.run() retries are per-call only

2. **Error aggregation**: When `on_error="continue"`, how surface partial failures?
   - Consider: `PipelineResult.errors: dict[str, Exception]`

3. **Streaming with ctx.run_stream()**: How does usage tracking work?
   - Usage only available at end of stream
   - Needs design if we add this

---

## File Change Summary

| File | Action | Phase |
|------|--------|-------|
| `fastroai/errors.py` | Create | 6 |
| `fastroai/pipelines/config.py` | Create | 2 |
| `fastroai/pipelines/base.py` | Modify | 1, 3 |
| `fastroai/pipelines/pipeline.py` | Modify | 4 |
| `fastroai/pipelines/executor.py` | Modify | 1, 4, 6 |
| `fastroai/pipelines/decorators.py` | Create | 5 |
| `fastroai/pipelines/__init__.py` | Modify | 1, 2, 5, 6 |
| `fastroai/agent/agent.py` | Modify | 1 |
| `fastroai/__init__.py` | Modify | 7 |
| `CLAUDE.md` | Modify | 7 |
| `tests/test_errors.py` | Create | 6 |
| `tests/test_config.py` | Create | 2 |
| `tests/test_step_context.py` | Create | 1, 3 |
| `tests/test_step_decorator.py` | Create | 5 |

---

*Last updated: 2025-12-16*

---

## Session Notes

### 2025-12-16 Session

**Completed:**
- Phase 1: Minimal ctx.run() - DONE
  - Added `_usage` and `usage` property to StepContext
  - Implemented `ctx.run(agent, message)` with automatic deps/tracer forwarding
  - Simplified executor `_extract_usage()` to just use `context.usage`
  - Updated `AgentStepWrapper` to use `ctx.run()` internally

- Phase 2: Config Classes - DONE
  - Created `fastroai/pipelines/config.py` with `StepConfig` and `PipelineConfig`
  - Added exports to `pipelines/__init__.py`

- Phase 6: Error Hierarchy - DONE
  - Created `fastroai/errors.py` with `FastroAIError`, `PipelineValidationError`, `CostBudgetExceededError`
  - Updated `StepExecutionError` to inherit from `FastroAIError`
  - Updated all validation errors to use `PipelineValidationError`
  - Fixed linting: renamed `CostBudgetExceeded` → `CostBudgetExceededError` (N818)

- Phase 5: @step Decorator - DONE
  - Created `fastroai/pipelines/decorators.py` with `@step` decorator and `_FunctionStep`
  - Supports both `@step` and `@step(timeout=30)` syntax
  - Works with sync and async functions
  - Carries `StepConfig` from decorator args
  - Works with `ctx.run()` for agent calls

- Phase 3: Enhanced ctx.run() with config - DONE
  - Added `config` parameter to StepContext
  - Enhanced `ctx.run()` with timeout, retries, cost_budget enforcement
  - Implemented `_execute_with_config()` with exponential backoff retry logic
  - Budget checked BEFORE each call (raises CostBudgetExceededError)
  - Per-call overrides via `ctx.run(agent, msg, timeout=..., retries=...)`

- Phase 4: Pipeline config integration - DONE
  - Added `config` and `step_configs` params to Pipeline constructor
  - Implemented config resolution in executor: pipeline → step class → step_configs
  - `_resolve_config()` merges configs with proper precedence
  - Tests verify full inheritance chain

- Phase 7: Polish & Documentation - DONE
  - Updated `fastroai/__init__.py` with new exports: `step`, `StepConfig`, `PipelineConfig`, error classes
  - Updated module docstring with new Pipeline example using `@step` and `ctx.run()`
  - Updated `CLAUDE.md` with three step patterns, `ctx.run()` docs, config inheritance, error hierarchy

**ALL PHASES COMPLETE! ✅**

**Final Status:**
- Test Coverage: **100%** (654 statements, 0 missed)
- Tests: 177 passed, 11 skipped
- Linting: All checks passed
- Type Check: No issues found in 20 source files

Note: 3 defensive/unreachable lines marked with `# pragma: no cover`:
- agent/agent.py:395 - awaitable raw_output (PydanticAI edge case)
- pipelines/base.py:277 - defensive RuntimeError (logically unreachable)
- pipelines/executor.py:135 - redundant cycle check (cycles caught by _validate())
