# Execution Plan: Evolution & Iteration Module Unification

**Branch:** `feature/iterative-feedback-pattern`
**Author:** Brian
**Status:** Draft
**Created:** 2025-12-11

---

## Executive Summary

This plan promotes the Evolution and Iteration modules from experimental add-ons to first-class citizens within the core orchestration engine. The key changes are:

1. **Unified Feedback Memory (The "Blackboard")** - A DuckDB-backed knowledge base that persists both iteration attempts and evolution programs
2. **Dynamic Mode Switching (Auto-Tuner)** - State-machine based triggering of phases based on runtime metrics
3. **Iterative Planning** - Replace custom debate logic with `IterativeSolver` + a Critic evaluator
4. **Adversarial Test Generation** - Use MAP-Elites to evolve tests that break the current best implementation

---

## Current State Analysis

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Orchestrator                                   │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌────────────────────────┐ │
│  │ Planning │→ │ Execution │→ │  Review  │→ │      Refinement        │ │
│  └──────────┘  └───────────┘  └──────────┘  └────────────────────────┘ │
│                                                         ↑               │
│                                                    (optional)           │
├─────────────────────────────────────────────────────────────────────────┤
│                    ISOLATED MODULES (Current)                           │
│  ┌────────────────────────────┐  ┌─────────────────────────────────┐   │
│  │      Evolution Module      │  │       Iteration Module          │   │
│  │  ┌────────────────────┐   │  │  ┌────────────────────┐        │   │
│  │  │ ProgramDatabase    │   │  │  │ SolutionHistory    │        │   │
│  │  │ (in-memory MAP-E)  │   │  │  │ (in-memory list)   │        │   │
│  │  └────────────────────┘   │  │  └────────────────────┘        │   │
│  └────────────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Findings

| Component | Current State | Problem |
|-----------|--------------|---------|
| `ProgramDatabase` | In-memory Map<id, Program>, island-based | State evaporates between runs |
| `SolutionHistory` | In-memory list of `SolutionAttempt` | No persistence, no cross-session learning |
| `AgentPerformanceTracker` | DuckDB-backed, workflow/agent metrics | Only stores summary stats, not solutions |
| `EvolutionPhase` | Standalone phase, manually triggered | Not integrated into auto-tuning workflow |
| `PlanningPhase._run_debate()` | Custom debate loop | Duplicates iteration logic |
| `ValidationResult` | Captures test results | No explicit performance vs correctness flags |

### Data Structure Comparison

**SolutionAttempt (Iteration):**
```python
@dataclass
class SolutionAttempt:
    iteration: int
    code: str | None
    output: str
    success: bool
    soft_score: float
    feedback: str
    error: str | None
    timestamp: datetime
    token_usage: int
    duration_seconds: float
    metadata: dict[str, Any]
```

**Program (Evolution):**
```python
@dataclass
class Program:
    id: str
    code: str
    metrics: ProgramMetrics  # Multi-dimensional: test_score, runtime_ms, etc.
    parent_ids: list[str]
    inspiration_ids: list[str]
    agent: str
    prompt_template: str
    diff_applied: str | None
    created_at: datetime
    is_valid: bool
    is_champion: bool
```

Both store code + metrics + timestamp + metadata. The key difference is `Program` has richer multi-dimensional metrics and lineage tracking.

---

## Part A: Unified Feedback Memory ("Blackboard")

### Objective

Consolidate `SolutionHistory` and `ProgramDatabase` into a single DuckDB-backed knowledge base that persists across sessions and can be queried for few-shot examples.

### Schema Design

**New Migration (Version 4):**

```sql
-- Migration 4: Unified Solutions Table
CREATE SEQUENCE IF NOT EXISTS seq_solutions;

CREATE TABLE IF NOT EXISTS solutions (
    id VARCHAR PRIMARY KEY,
    workflow_id VARCHAR,                    -- Link to workflows table
    task_hash VARCHAR NOT NULL,             -- Hash of task for similarity lookup
    task_preview TEXT,                      -- Truncated task text

    -- Solution content
    code_content TEXT,                      -- The actual code/solution
    diff_applied TEXT,                      -- Diff that created this from parent

    -- Classification
    solution_type VARCHAR NOT NULL,         -- 'iteration_attempt' | 'evolution_program'
    agent VARCHAR NOT NULL,                 -- Which agent produced this

    -- Metrics (unified from both modules)
    success BOOLEAN NOT NULL,
    overall_score DOUBLE NOT NULL,
    test_score DOUBLE,
    tests_passed INTEGER,
    tests_total INTEGER,
    lint_score DOUBLE,
    runtime_ms DOUBLE,
    memory_mb DOUBLE,

    -- Performance metrics for auto-tuner
    needs_optimization BOOLEAN DEFAULT FALSE,  -- Flag for auto-tuner
    performance_issue VARCHAR,                  -- 'slow' | 'memory' | 'timeout' | NULL

    -- Feedback and context
    feedback_summary TEXT,                  -- Structured feedback for LLM
    error_message TEXT,

    -- Lineage (for evolution)
    parent_solution_id VARCHAR,
    inspiration_ids JSON,                   -- Array of solution IDs
    generation INTEGER DEFAULT 0,

    -- Status flags
    is_valid BOOLEAN DEFAULT FALSE,
    is_champion BOOLEAN DEFAULT FALSE,

    -- Timestamps and usage
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluated_at TIMESTAMP,
    token_usage INTEGER,
    duration_seconds DOUBLE,

    -- Tags for flexible querying
    tags JSON                               -- Array of strings for categorization
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_solutions_task_hash ON solutions(task_hash);
CREATE INDEX IF NOT EXISTS idx_solutions_workflow ON solutions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_solutions_score ON solutions(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_solutions_type ON solutions(solution_type);
CREATE INDEX IF NOT EXISTS idx_solutions_agent ON solutions(agent);
CREATE INDEX IF NOT EXISTS idx_solutions_success ON solutions(success);
CREATE INDEX IF NOT EXISTS idx_solutions_champion ON solutions(is_champion) WHERE is_champion = TRUE;

-- Niche table for MAP-elites behavioral dimensions
CREATE TABLE IF NOT EXISTS solution_niches (
    niche_key VARCHAR PRIMARY KEY,          -- e.g., "test_score:0.9,runtime:fast"
    solution_id VARCHAR NOT NULL REFERENCES solutions(id),
    dimensions JSON NOT NULL,               -- The actual dimension values
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Implementation Steps

#### Step A.1: Create `SolutionStore` DAL

**File:** `src/deliberate/tracking/solution_store.py`

```python
@dataclass
class SolutionRecord:
    """Unified record for both iteration attempts and evolution programs."""
    id: str
    workflow_id: str | None
    task_hash: str
    code_content: str | None
    diff_applied: str | None
    solution_type: Literal["iteration_attempt", "evolution_program"]
    agent: str
    success: bool
    overall_score: float
    metrics: dict[str, Any]  # Flexible metrics storage
    feedback_summary: str | None
    parent_solution_id: str | None
    generation: int
    is_champion: bool
    tags: list[str]
    created_at: datetime


class SolutionStore:
    """DuckDB-backed solution storage with MAP-elites niche support."""

    def __init__(self, tracker: AgentPerformanceTracker):
        self._tracker = tracker
        self._conn = tracker._conn  # Reuse tracker's connection

    def add(self, record: SolutionRecord) -> str:
        """Add a solution, updating niche if it's a new champion."""
        ...

    def get_by_id(self, solution_id: str) -> SolutionRecord | None:
        """Retrieve a solution by ID."""
        ...

    def get_best_for_task(
        self,
        task_hash: str,
        limit: int = 5,
        min_score: float = 0.5
    ) -> list[SolutionRecord]:
        """Get top solutions for similar tasks (for few-shot prompting)."""
        ...

    def get_champions(self, limit: int = 10) -> list[SolutionRecord]:
        """Get current champion solutions across all niches."""
        ...

    def sample_for_evolution(
        self,
        task_hash: str,
        num_parents: int = 2,
        num_inspirations: int = 3,
        temperature: float = 1.0
    ) -> tuple[list[SolutionRecord], list[SolutionRecord]]:
        """Sample parents and inspirations for evolution."""
        ...

    def update_niche(self, solution_id: str, niche_key: str, dimensions: dict):
        """Update MAP-elites niche with new champion if better."""
        ...

    def cleanup_old_solutions(self, max_age_days: int = 30, keep_champions: bool = True):
        """Remove old non-champion solutions."""
        ...
```

#### Step A.2: Refactor `ProgramDatabase`

**File:** `src/deliberate/evolution/database.py`

Update `ProgramDatabase` to delegate storage to `SolutionStore` while keeping the in-memory island sampling logic for performance:

```python
class ProgramDatabase:
    """MAP-elites style database backed by SolutionStore."""

    def __init__(
        self,
        config: DatabaseConfig,
        solution_store: SolutionStore | None = None,  # NEW: Optional persistence
        task_hash: str | None = None,
    ):
        self.config = config
        self._store = solution_store
        self._task_hash = task_hash

        # Keep in-memory structures for fast sampling during evolution
        self._islands: list[IslandPopulation] = [...]
        self._programs: dict[str, Program] = {}

        # Load champions from store if available
        if self._store and self._task_hash:
            self._load_from_store()

    def _load_from_store(self):
        """Load relevant solutions from persistent store."""
        champions = self._store.get_best_for_task(self._task_hash, limit=20)
        for record in champions:
            program = self._record_to_program(record)
            self._add_to_memory(program)

    def add(self, program: Program) -> bool:
        """Add program to database and optionally persist."""
        added = self._add_to_memory(program)
        if added and self._store:
            record = self._program_to_record(program)
            self._store.add(record)
        return added

    def _program_to_record(self, program: Program) -> SolutionRecord:
        """Convert Program to SolutionRecord for persistence."""
        ...

    def _record_to_program(self, record: SolutionRecord) -> Program:
        """Convert SolutionRecord to Program for in-memory use."""
        ...
```

#### Step A.3: Refactor `SolutionHistory`

**File:** `src/deliberate/iteration/history.py`

Make `SolutionHistory` a view over `SolutionStore`:

```python
class SolutionHistory:
    """Accumulates solution attempts, optionally backed by SolutionStore."""

    def __init__(
        self,
        solution_store: SolutionStore | None = None,
        workflow_id: str | None = None,
        task_hash: str | None = None,
    ):
        self._store = solution_store
        self._workflow_id = workflow_id
        self._task_hash = task_hash

        # In-memory buffer for current session
        self._attempts: list[SolutionAttempt] = []

    def add(self, attempt: SolutionAttempt) -> None:
        """Add attempt to history and optionally persist."""
        self._attempts.append(attempt)
        if self._store:
            record = self._attempt_to_record(attempt)
            self._store.add(record)

    def get_historical_context(self, limit: int = 3) -> list[SolutionAttempt]:
        """Get successful attempts from similar past tasks for few-shot."""
        if not self._store or not self._task_hash:
            return []

        records = self._store.get_best_for_task(
            self._task_hash,
            limit=limit,
            min_score=0.8
        )
        return [self._record_to_attempt(r) for r in records]
```

#### Step A.4: Update PlanningPhase to Use Historical Context

**File:** `src/deliberate/phases/planning.py`

```python
class PlanningPhase:
    def __init__(
        self,
        ...,
        solution_store: SolutionStore | None = None,  # NEW
    ):
        self._solution_store = solution_store

    async def _build_prompt(self, task: str, context: JuryContext) -> str:
        """Build planning prompt with optional historical examples."""
        base_prompt = self._base_prompt_template.format(task=task)

        if self._solution_store:
            task_hash = hash_task(task)
            examples = self._solution_store.get_best_for_task(task_hash, limit=2)
            if examples:
                few_shot = self._format_examples(examples)
                base_prompt = f"{few_shot}\n\n{base_prompt}"

        return base_prompt
```

### Validation Criteria

- [ ] Migration 4 applies cleanly to existing databases
- [ ] `SolutionStore` can round-trip `SolutionRecord` through DuckDB
- [ ] `ProgramDatabase` preserves existing behavior with `solution_store=None`
- [ ] `SolutionHistory` preserves existing behavior with `solution_store=None`
- [ ] Few-shot examples improve plan quality (measured via A/B test)
- [ ] Evolution can seed from historical champions

---

## Part B: Dynamic Mode Switching ("Auto-Tuner")

### Objective

Enable the Orchestrator to automatically trigger Evolution mode when a solution passes functionality tests but fails performance benchmarks.

### Design

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Orchestrator.run()                              │
│                                                                          │
│   Planning → Execution → Validation → [AutoTuner Decision] → Review     │
│                               │                │                         │
│                               ▼                ▼                         │
│                      ┌─────────────┐    ┌─────────────┐                 │
│                      │ValidationResult   │ TriggerPolicy│                 │
│                      │.needs_optimization │  (config)   │                 │
│                      └─────────────┘    └─────────────┘                 │
│                               │                │                         │
│                               └───────┬────────┘                         │
│                                       ▼                                  │
│                              ┌─────────────────┐                         │
│                              │ Evolution Phase │                         │
│                              │ (if triggered)  │                         │
│                              └─────────────────┘                         │
└──────────────────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step B.1: Extend `ValidationResult`

**File:** `src/deliberate/validation/types.py`

```python
class PerformanceIssue(Enum):
    """Types of performance issues detected."""
    NONE = "none"
    SLOW_EXECUTION = "slow_execution"     # Runtime > threshold
    HIGH_MEMORY = "high_memory"           # Memory > threshold
    TIMEOUT = "timeout"                   # Hit timeout limit
    FLAKY = "flaky"                       # Intermittent failures


@dataclass
class ValidationResult:
    passed: bool
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    tests_run: int
    tests_passed: int
    tests_failed: int
    tests_skipped: int
    test_cases: list[CaseResult]
    regression_detected: bool = False

    # NEW: Performance metrics
    performance_issue: PerformanceIssue = PerformanceIssue.NONE
    needs_optimization: bool = False
    slowest_tests: list[tuple[str, float]] = field(default_factory=list)  # (name, duration)

    @property
    def correctness_passed(self) -> bool:
        """Tests passed (ignoring performance)."""
        return self.passed and not self.regression_detected

    @property
    def is_slow(self) -> bool:
        """Check if execution was slower than expected."""
        return self.performance_issue in (
            PerformanceIssue.SLOW_EXECUTION,
            PerformanceIssue.TIMEOUT
        )
```

#### Step B.2: Update `ValidationRunner` to Detect Performance Issues

**File:** `src/deliberate/validation/runner.py`

```python
class ValidationRunner:
    def __init__(
        self,
        ...,
        latency_threshold_ms: float = 500.0,  # NEW
        memory_threshold_mb: float = 512.0,   # NEW
    ):
        self._latency_threshold = latency_threshold_ms
        self._memory_threshold = memory_threshold_mb

    async def run(self, ...) -> ValidationResult:
        result = await self._execute_tests(...)

        # Analyze performance
        result = self._analyze_performance(result)
        return result

    def _analyze_performance(self, result: ValidationResult) -> ValidationResult:
        """Detect performance issues in passing tests."""
        if not result.passed:
            return result  # Don't analyze perf on failing tests

        # Check overall duration
        duration_ms = result.duration_seconds * 1000
        if duration_ms > self._latency_threshold:
            result.performance_issue = PerformanceIssue.SLOW_EXECUTION
            result.needs_optimization = True

        # Find slowest tests
        sorted_cases = sorted(
            result.test_cases,
            key=lambda c: c.duration_seconds,
            reverse=True
        )
        result.slowest_tests = [
            (c.name, c.duration_seconds)
            for c in sorted_cases[:5]
        ]

        return result
```

#### Step B.3: Add `TriggerPolicy` Configuration

**File:** `src/deliberate/config.py`

```python
class TriggerPolicy(Enum):
    """Action to take on slow execution."""
    WARN = "warn"       # Log warning, continue normally
    FAIL = "fail"       # Treat as failure
    EVOLVE = "evolve"   # Trigger evolution phase


class AutoTunerConfig(BaseModel):
    """Configuration for automatic mode switching."""

    enabled: bool = False

    # Trigger conditions
    on_slow_execution: TriggerPolicy = TriggerPolicy.WARN
    latency_threshold_ms: float = 500.0
    memory_threshold_mb: float = 512.0

    # Limits to prevent infinite loops
    max_evolution_attempts: int = 3
    max_total_iterations: int = 10  # Across all modes

    # Evolution target when triggered
    optimization_target: Literal["latency", "memory", "token_count"] = "latency"


class WorkflowConfig(BaseModel):
    planning: PlanningConfig = Field(default_factory=PlanningConfig)
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    review: ReviewConfig = Field(default_factory=ReviewConfig)
    refinement: RefinementConfig = Field(default_factory=RefinementConfig)
    evolution: EvolutionWorkflowConfig = Field(default_factory=EvolutionWorkflowConfig)
    auto_tuner: AutoTunerConfig = Field(default_factory=AutoTunerConfig)  # NEW
    require_tests: bool = False
```

#### Step B.4: Update Orchestrator with Auto-Tuner Logic

**File:** `src/deliberate/orchestrator.py`

```python
class Orchestrator:
    async def _run_workflow(self, task: str, context: JuryContext) -> WorkflowResult:
        # ... existing planning and execution ...

        execution_result = await self._execution_phase.run(...)

        # NEW: Auto-tuner decision point
        if self._should_trigger_evolution(execution_result):
            evolution_result = await self._run_evolution_for_optimization(
                task=task,
                execution_result=execution_result,
                target=self.config.workflow.auto_tuner.optimization_target,
            )
            if evolution_result.success and evolution_result.best_program:
                # Replace execution result with evolved version
                execution_result = self._update_result_with_evolution(
                    execution_result,
                    evolution_result
                )

        # Continue with review...
        review_result = await self._review_phase.run(...)

    def _should_trigger_evolution(self, result: ExecutionResult) -> bool:
        """Determine if we should trigger evolution based on policy."""
        config = self.config.workflow.auto_tuner

        if not config.enabled:
            return False

        if not result.validation_result:
            return False

        validation = result.validation_result

        # Check policy
        if config.on_slow_execution == TriggerPolicy.EVOLVE:
            if validation.needs_optimization:
                logger.info(
                    f"Auto-tuner: Triggering evolution for {validation.performance_issue.value}"
                )
                return True

        return False

    async def _run_evolution_for_optimization(
        self,
        task: str,
        execution_result: ExecutionResult,
        target: str,
    ) -> EvolutionResult:
        """Run evolution phase with specific optimization target."""
        # Create evolution phase with performance-focused config
        evo_config = self._build_optimization_config(target)

        evolution_phase = EvolutionPhase(
            agents=self._adapters,
            budget_tracker=self._budget,
            max_iterations=evo_config.max_iterations,
            target_score=evo_config.target_score,
            # ... other params
        )

        return await evolution_phase.run(
            task=self._build_optimization_task(task, target),
            execution_result=execution_result,
            working_dir=execution_result.worktree_path,
        )

    def _build_optimization_task(self, original_task: str, target: str) -> str:
        """Augment task with optimization instructions."""
        optimization_prompts = {
            "latency": "Optimize the following code for execution speed while maintaining correctness.",
            "memory": "Optimize the following code for memory efficiency while maintaining correctness.",
            "token_count": "Simplify the following code to reduce complexity while maintaining correctness.",
        }
        return f"{optimization_prompts[target]}\n\nOriginal task:\n{original_task}"
```

### Validation Criteria

- [ ] `ValidationResult.needs_optimization` is set correctly for slow tests
- [ ] Auto-tuner triggers evolution only when policy is `EVOLVE`
- [ ] Evolution phase receives optimization-specific prompts
- [ ] Loop counter prevents infinite evolution attempts
- [ ] Evolved code replaces original in execution result
- [ ] Budget is properly tracked across modes

---

## Part C: Iterative Planning

### Objective

Replace the custom debate logic in `PlanningPhase` with an `IterativeSolver` instance using a `PlanReviewEvaluator` (Critic agent).

### Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PlanningPhase (refactored)                       │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐ │
│   │                    IterativeSolver<Plan>                         │ │
│   │                                                                  │ │
│   │  ┌────────────────┐  ┌─────────────────────┐  ┌───────────────┐│ │
│   │  │ PlanGenerator  │→ │ PlanReviewEvaluator │→ │ FeedbackBuilder││ │
│   │  │   (Planner)    │  │     (Critic LLM)    │  │               ││ │
│   │  └────────────────┘  └─────────────────────┘  └───────────────┘│ │
│   │                              │                                   │ │
│   │                              ▼                                   │ │
│   │                    SolutionHistory<Plan>                         │ │
│   │                   (persisted to DuckDB)                          │ │
│   └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step C.1: Create `PlanReviewEvaluator`

**File:** `src/deliberate/iteration/evaluators.py` (new file)

```python
from deliberate.iteration.types import SolutionAttempt, FeedbackContext
from deliberate.types import Plan
from abc import ABC, abstractmethod


class PlanReviewEvaluator(SolutionEvaluator[Plan]):
    """Evaluator that uses a Critic LLM to score plans.

    The 'test' is not running code, but running a Critic Agent that
    scores the plan on feasibility, completeness, and risk.
    """

    def __init__(
        self,
        critic_agent: ModelAdapter,
        criteria: list[str] | None = None,
        success_threshold: float = 0.9,
    ):
        self._critic = critic_agent
        self._criteria = criteria or [
            "feasibility",      # Is the plan achievable?
            "completeness",     # Does it cover all requirements?
            "risk",             # What could go wrong?
            "clarity",          # Is it well-structured?
        ]
        self._success_threshold = success_threshold

    async def evaluate(self, plan: Plan) -> FeedbackContext:
        """Have critic agent evaluate the plan."""
        prompt = self._build_critic_prompt(plan)

        response = await self._critic.complete(prompt)

        # Parse structured response
        scores, feedback = self._parse_critic_response(response)

        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)

        return FeedbackContext(
            expected="A feasible, complete, low-risk plan",
            actual=plan.summary,
            match=overall_score >= self._success_threshold,
            soft_score=overall_score,
            diff=None,
            errors=self._extract_issues(feedback),
            metadata={
                "scores": scores,
                "feedback": feedback,
            }
        )

    def _build_critic_prompt(self, plan: Plan) -> str:
        """Build prompt for critic agent."""
        criteria_text = "\n".join(f"- {c}" for c in self._criteria)

        return f"""You are a critical reviewer of implementation plans.

Evaluate this plan on the following criteria (score each 0.0-1.0):
{criteria_text}

PLAN:
{plan.content}

Respond in JSON format:
{{
    "scores": {{"feasibility": 0.X, "completeness": 0.X, ...}},
    "issues": ["issue 1", "issue 2", ...],
    "suggestions": ["suggestion 1", ...]
}}
"""

    def _parse_critic_response(self, response: str) -> tuple[dict[str, float], str]:
        """Parse JSON response from critic."""
        import json
        try:
            data = json.loads(response)
            return data.get("scores", {}), json.dumps(data, indent=2)
        except json.JSONDecodeError:
            # Fallback: extract scores from text
            return {"overall": 0.5}, response
```

#### Step C.2: Create `PlanExtractor`

**File:** `src/deliberate/iteration/extractors.py` (new file)

```python
class PlanExtractor(SolutionExtractor[Plan]):
    """Extract Plan from LLM response."""

    def extract(self, response: str, context: dict[str, Any]) -> Plan | None:
        """Extract structured plan from response."""
        # Try to parse structured format first
        if "<plan>" in response:
            return self._extract_xml_plan(response, context)

        # Fall back to treating entire response as plan content
        return Plan(
            agent=context.get("agent", "unknown"),
            content=response.strip(),
            summary=self._extract_summary(response),
            estimated_files=[],
            reasoning=None,
        )

    def _extract_xml_plan(self, response: str, context: dict) -> Plan:
        """Extract plan from XML tags."""
        import re

        plan_match = re.search(r"<plan>(.*?)</plan>", response, re.DOTALL)
        summary_match = re.search(r"<summary>(.*?)</summary>", response, re.DOTALL)
        reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", response, re.DOTALL)

        return Plan(
            agent=context.get("agent", "unknown"),
            content=plan_match.group(1).strip() if plan_match else response,
            summary=summary_match.group(1).strip() if summary_match else "",
            estimated_files=[],
            reasoning=reasoning_match.group(1).strip() if reasoning_match else None,
        )
```

#### Step C.3: Refactor `PlanningPhase` to Use `IterativeSolver`

**File:** `src/deliberate/phases/planning.py`

```python
class PlanningPhase:
    def __init__(
        self,
        adapters: dict[str, ModelAdapter],
        config: PlanningConfig,
        budget_tracker: BudgetTracker,
        solution_store: SolutionStore | None = None,
    ):
        self._adapters = adapters
        self._config = config
        self._budget = budget_tracker
        self._solution_store = solution_store

    async def run(self, task: str, context: JuryContext) -> Plan:
        """Run planning phase with iterative refinement."""

        if self._config.debate.enabled:
            # NEW: Use IterativeSolver for debate
            return await self._run_iterative_planning(task, context)
        else:
            # Original: collect and select
            return await self._collect_and_select(task, context)

    async def _run_iterative_planning(self, task: str, context: JuryContext) -> Plan:
        """Run iterative planning with critic feedback."""

        # Get planner and critic agents
        planner_name = self._config.agents[0] if self._config.agents else "default"
        critic_name = self._config.debate.critic or planner_name  # Can be same agent

        planner = self._adapters[planner_name]
        critic = self._adapters[critic_name]

        # Create evaluator
        evaluator = PlanReviewEvaluator(
            critic_agent=critic,
            success_threshold=0.9,
        )

        # Create solver
        solver = IterativeSolver[Plan](
            agent=planner,
            evaluator=evaluator,
            extractor=PlanExtractor(),
            feedback_builder=PlanFeedbackBuilder(),
            config=IterationConfig(
                max_iterations=self._config.debate.rounds,
                success_threshold=0.9,
            ),
            solution_history=SolutionHistory(
                solution_store=self._solution_store,
                task_hash=hash_task(task),
            ),
        )

        # Run iterative planning
        result = await solver.solve(
            task=task,
            system_prompt=self._build_system_prompt(context),
        )

        if result.success and result.best_attempt:
            return result.best_attempt.solution  # type: ignore

        # Return best attempt even if not perfect
        if result.best_attempt:
            return result.best_attempt.solution  # type: ignore

        raise PlanningError("Failed to generate a valid plan")

    # DEPRECATED: Remove in future version
    async def _run_debate(self, task: str, plans: list[Plan], context: JuryContext) -> Plan:
        """Legacy debate logic - replaced by _run_iterative_planning."""
        warnings.warn(
            "_run_debate is deprecated, use _run_iterative_planning instead",
            DeprecationWarning
        )
        # ... keep old implementation for backward compatibility ...
```

### Validation Criteria

- [ ] `PlanReviewEvaluator` correctly parses critic JSON responses
- [ ] `IterativeSolver<Plan>` terminates when critic score > 0.9
- [ ] Plan quality improves over iterations (measured via review scores)
- [ ] Legacy `_run_debate` behavior preserved when `debate.use_legacy=True`
- [ ] Budget properly tracked for critic calls
- [ ] History persisted to `SolutionStore`

---

## Part D: Adversarial Test Generation

### Objective

Use the Evolution engine to generate tests that break the current best implementation, creating an adversarial improvement loop.

### Design

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     Adversarial Test Loop                                │
│                                                                          │
│  Step 1: Evolve Code     Step 2: Evolve Tests    Step 3: Repeat         │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐  │
│  │ Code Population   │   │ Test Population   │   │ Merge new tests   │  │
│  │ Goal: Pass tests  │ → │ Goal: Break code  │ → │ Go to Step 1      │  │
│  │ Fitness: test_score   │ Fitness: kill_rate│   │                   │  │
│  └───────────────────┘   └───────────────────┘   └───────────────────┘  │
│                                                                          │
│  Termination: max_cycles OR no new breaking tests found                 │
└──────────────────────────────────────────────────────────────────────────┘
```

### Implementation Steps

#### Step D.1: Extend `ProgramMetrics` for Tests

**File:** `src/deliberate/evolution/types.py`

```python
@dataclass
class ProgramMetrics:
    # ... existing fields ...

    # NEW: Test-specific metrics (when program is a test file)
    champion_kill_rate: float = 0.0  # How many code solutions this test broke
    is_valid_test: bool = False       # Verified by judge as valid business logic
    test_cases_generated: int = 0     # Number of test cases in this file
    covers_edge_cases: list[str] = field(default_factory=list)
```

#### Step D.2: Create `TestGenerationPromptBuilder`

**File:** `src/deliberate/evolution/prompts.py`

```python
class TestGenerationPromptBuilder:
    """Build prompts for evolving test files."""

    def build_evolution_prompt(
        self,
        current_champion_code: str,
        parent_test: str | None,
        inspiration_tests: list[str],
        task_spec: str,
    ) -> str:
        return f"""You are an adversarial test generator. Your goal is to write tests that:
1. Are valid Python test files using pytest
2. Represent legitimate business requirements from the specification
3. BREAK the current champion implementation

IMPORTANT: Tests must be valid requirements, not hallucinated edge cases.
Only write tests for behavior explicitly stated or clearly implied by the spec.

TASK SPECIFICATION:
{task_spec}

CURRENT CHAMPION CODE (to break):
```python
{current_champion_code}
```

{self._format_parent_context(parent_test)}
{self._format_inspirations(inspiration_tests)}

Generate a test file that exposes a bug or missing feature in the champion.

OUTPUT FORMAT:
```python
# test_adversarial.py
import pytest
...
```
"""

    def _format_parent_context(self, parent: str | None) -> str:
        if not parent:
            return ""
        return f"""
PARENT TEST (evolve from this):
```python
{parent}
```
"""

    def _format_inspirations(self, tests: list[str]) -> str:
        if not tests:
            return ""

        formatted = "\n\n".join(f"```python\n{t}\n```" for t in tests)
        return f"""
INSPIRATION TESTS (successful test patterns):
{formatted}
"""
```

#### Step D.3: Create `TestValidationEvaluator`

**File:** `src/deliberate/evolution/evaluators.py`

```python
class TestValidationEvaluator:
    """Evaluator for adversarial test files.

    A test has high fitness if:
    1. It is valid Python (syntax check)
    2. It represents valid business requirements (judge check)
    3. It fails against the current champion code (kill check)
    """

    def __init__(
        self,
        champion_code_path: Path,
        task_spec: str,
        judge_agent: ModelAdapter | None = None,
        working_dir: Path,
    ):
        self._champion_path = champion_code_path
        self._task_spec = task_spec
        self._judge = judge_agent
        self._working_dir = working_dir

    async def evaluate(self, test_code: str) -> ProgramMetrics:
        """Evaluate a generated test file."""
        metrics = ProgramMetrics()

        # Level 1: Syntax check
        if not self._is_valid_python(test_code):
            metrics.highest_level_passed = EvaluationLevel.SYNTAX
            return metrics

        # Level 2: Judge validation (is this a valid requirement?)
        if self._judge:
            is_valid = await self._verify_with_judge(test_code)
            if not is_valid:
                metrics.is_valid_test = False
                return metrics
            metrics.is_valid_test = True

        # Level 3: Run against champion (we WANT it to fail)
        kill_result = await self._run_against_champion(test_code)
        metrics.champion_kill_rate = kill_result.failure_rate

        # Higher kill rate = better test
        metrics.test_score = metrics.champion_kill_rate

        return metrics

    async def _verify_with_judge(self, test_code: str) -> bool:
        """Have judge verify test represents valid requirements."""
        prompt = f"""You are a test validation judge.

Determine if this test file represents VALID business requirements based on the specification.
A test is INVALID if it:
- Tests behavior not mentioned in the spec
- Makes up edge cases not implied by the spec
- Has hallucinated assertions

SPECIFICATION:
{self._task_spec}

TEST FILE:
```python
{test_code}
```

Respond with JSON:
{{"valid": true/false, "reasoning": "..."}}
"""
        response = await self._judge.complete(prompt)
        try:
            import json
            data = json.loads(response)
            return data.get("valid", False)
        except:
            return False

    async def _run_against_champion(self, test_code: str) -> KillResult:
        """Run test against champion code and measure failures."""
        # Write test file
        test_path = self._working_dir / "test_adversarial.py"
        test_path.write_text(test_code)

        # Run pytest
        result = await asyncio.create_subprocess_exec(
            "pytest", str(test_path), "-v", "--tb=short",
            cwd=str(self._working_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await result.communicate()

        # Parse results
        return self._parse_pytest_output(stdout.decode(), stderr.decode())
```

#### Step D.4: Create `AdversarialTestLoop`

**File:** `src/deliberate/evolution/adversarial.py` (new file)

```python
@dataclass
class AdversarialConfig:
    """Configuration for adversarial test generation."""
    max_cycles: int = 3                     # Max code-test cycles
    max_test_evolution_iterations: int = 10 # Iterations per test evolution
    min_kill_rate: float = 0.1              # Min kill rate to accept test
    max_new_tests_per_cycle: int = 3        # Tests to add per cycle


class AdversarialTestLoop:
    """Orchestrates adversarial code-test co-evolution."""

    def __init__(
        self,
        agents: dict[str, ModelAdapter],
        task_spec: str,
        working_dir: Path,
        budget_tracker: BudgetTracker,
        config: AdversarialConfig,
        solution_store: SolutionStore | None = None,
    ):
        self._agents = agents
        self._task_spec = task_spec
        self._working_dir = working_dir
        self._budget = budget_tracker
        self._config = config
        self._store = solution_store

    async def run(
        self,
        initial_code: str,
        initial_tests: str,
    ) -> AdversarialResult:
        """Run adversarial loop."""

        current_code = initial_code
        current_tests = initial_tests
        cycles_completed = 0
        new_tests_found = []

        for cycle in range(self._config.max_cycles):
            logger.info(f"Adversarial cycle {cycle + 1}/{self._config.max_cycles}")

            # Step 1: Evolve code to pass current tests
            code_evolution = await self._evolve_code(current_code, current_tests)
            if not code_evolution.success:
                logger.warning(f"Code evolution failed in cycle {cycle}")
                break

            current_code = code_evolution.best_program.code

            # Step 2: Evolve tests to break current code
            test_evolution = await self._evolve_tests(current_code, current_tests)

            # Filter for valid, breaking tests
            breaking_tests = [
                t for t in test_evolution.all_programs
                if t.metrics.is_valid_test and t.metrics.champion_kill_rate > self._config.min_kill_rate
            ]

            if not breaking_tests:
                logger.info("No new breaking tests found - adversarial loop complete")
                break

            # Step 3: Add best breaking tests to suite
            for test in breaking_tests[:self._config.max_new_tests_per_cycle]:
                new_tests_found.append(test)
                current_tests = self._merge_test(current_tests, test.code)

            cycles_completed = cycle + 1

        return AdversarialResult(
            final_code=current_code,
            final_tests=current_tests,
            cycles_completed=cycles_completed,
            new_tests_added=len(new_tests_found),
            test_programs=new_tests_found,
        )

    async def _evolve_code(self, code: str, tests: str) -> EvolutionResult:
        """Evolve code to pass tests."""
        # Use standard evolution with TDDEvaluator
        ...

    async def _evolve_tests(self, champion_code: str, current_tests: str) -> EvolutionResult:
        """Evolve tests to break champion code."""

        # Create test-specific database
        db = ProgramDatabase(
            config=DatabaseConfig(
                niche_dimensions=["champion_kill_rate", "test_cases_generated"]
            ),
            solution_store=self._store,
        )

        # Create test evaluator
        evaluator = TestValidationEvaluator(
            champion_code_path=self._working_dir / "solution.py",
            task_spec=self._task_spec,
            judge_agent=self._get_judge_agent(),
            working_dir=self._working_dir,
        )

        # Create evolution controller
        controller = EvolutionController(
            database=db,
            agents=self._agents,
            evaluator=evaluator,
            config=EvolutionConfig(
                max_iterations=self._config.max_test_evolution_iterations,
                target_score=1.0,  # 100% kill rate (unlikely, but aspirational)
            ),
            prompt_builder=TestGenerationPromptBuilder(),
        )

        return await controller.evolve(
            task=f"Generate tests that break this code:\n{champion_code}",
            seed_program=current_tests,
            working_dir=self._working_dir,
        )
```

### Validation Criteria

- [ ] `TestValidationEvaluator` correctly identifies valid vs hallucinated tests
- [ ] Kill rate is calculated accurately from pytest output
- [ ] Adversarial loop terminates when no new breaking tests found
- [ ] Budget tracked across both code and test evolution
- [ ] Judge validation prevents nonsense tests from being added
- [ ] New tests are properly merged into test suite

---

## Risk Mitigation

### Infinite Loops

**Mitigation:**
- Hard limit on `max_total_iterations` in `AutoTunerConfig`
- Cycle counter in `AdversarialTestLoop`
- Budget tracker enforced across all modes
- State machine approach with explicit terminal states

```python
class WorkflowState(Enum):
    PLANNING = "planning"
    EXECUTING = "executing"
    OPTIMIZING = "optimizing"  # Evolution for performance
    REVIEWING = "reviewing"
    REFINING = "refining"
    COMPLETE = "complete"
    FAILED = "failed"

# Allowed transitions (prevent loops)
ALLOWED_TRANSITIONS = {
    WorkflowState.PLANNING: {WorkflowState.EXECUTING, WorkflowState.FAILED},
    WorkflowState.EXECUTING: {WorkflowState.OPTIMIZING, WorkflowState.REVIEWING, WorkflowState.FAILED},
    WorkflowState.OPTIMIZING: {WorkflowState.REVIEWING, WorkflowState.FAILED},  # Only one chance
    WorkflowState.REVIEWING: {WorkflowState.REFINING, WorkflowState.COMPLETE, WorkflowState.FAILED},
    WorkflowState.REFINING: {WorkflowState.REVIEWING, WorkflowState.COMPLETE, WorkflowState.FAILED},
}
```

### Token Budget

**Mitigation:**
- Strict budget tracking with reserved pools
- Adversarial testing gets dedicated budget allocation (not unlimited)
- Early termination if budget < threshold for next phase

```python
class BudgetAllocation:
    """Pre-allocate budget for each workflow phase."""
    planning_pct: float = 0.15
    execution_pct: float = 0.35
    evolution_pct: float = 0.20  # Only used if triggered
    review_pct: float = 0.15
    refinement_pct: float = 0.15
    adversarial_pct: float = 0.10  # From evolution pool
```

### Context Window

**Mitigation:**
- `SolutionStore.get_best_for_task()` uses score-based ranking, not recency
- Limit to top-k examples (configurable, default 3)
- Use task_hash similarity for relevance filtering
- Compress feedback summaries before storing

```python
# In SolutionStore
def get_best_for_task(self, task_hash: str, limit: int = 3) -> list[SolutionRecord]:
    """Get top solutions, not all solutions."""
    return self._conn.execute("""
        SELECT * FROM solutions
        WHERE task_hash = ?
          AND success = TRUE
          AND overall_score > 0.7
        ORDER BY overall_score DESC
        LIMIT ?
    """, [task_hash, limit]).fetchall()
```

---

## Implementation Order

### Phase 1: Foundation (Part A)
1. Add migration 4 to `migrations.py`
2. Implement `SolutionStore` with tests
3. Refactor `ProgramDatabase` to use store (backward compatible)
4. Refactor `SolutionHistory` to use store (backward compatible)

### Phase 2: Auto-Tuner (Part B)
1. Extend `ValidationResult` with performance metrics
2. Update `ValidationRunner` to detect performance issues
3. Add `AutoTunerConfig` to config schema
4. Implement auto-tuner logic in Orchestrator

### Phase 3: Iterative Planning (Part C)
1. Create `PlanReviewEvaluator`
2. Create `PlanExtractor`
3. Refactor `PlanningPhase` to use `IterativeSolver`
4. Deprecate `_run_debate`

### Phase 4: Adversarial Tests (Part D)
1. Extend `ProgramMetrics` for tests
2. Create `TestGenerationPromptBuilder`
3. Create `TestValidationEvaluator`
4. Implement `AdversarialTestLoop`
5. Integrate into workflow (optional phase)

---

## Testing Strategy

### Unit Tests

```
tests/unit/
├── test_solution_store.py          # Part A
├── test_program_database_persistence.py
├── test_validation_performance.py  # Part B
├── test_plan_review_evaluator.py   # Part C
├── test_adversarial_evaluator.py   # Part D
```

### Integration Tests

```
tests/integration/
├── test_unified_memory_e2e.py      # A: Full persistence cycle
├── test_auto_tuner_triggers.py     # B: Slow code triggers evolution
├── test_iterative_planning.py      # C: Critic feedback improves plans
├── test_adversarial_loop.py        # D: Full code-test co-evolution
```

### Live Tests

```
tests/live/
├── test_real_slow_code.py          # B: Actual slow code optimization
├── test_real_adversarial.py        # D: Real adversarial test generation
```

---

## Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Plan quality (review score) | 0.7 | 0.85 | Average score from critics |
| Evolution reuse rate | 0% | 30% | % of runs using historical solutions |
| Auto-tuner trigger rate | N/A | < 20% | % of runs where slow code detected |
| Adversarial test kill rate | N/A | > 50% | % of generated tests that break champion |
| Token cost per run | Baseline | < +15% | Additional cost from new features |

---

## Open Questions

1. **Schema migration strategy**: Should we support rollback for migration 4? DuckDB doesn't have great migration tooling.

2. **Task hash similarity**: Should `task_hash` be exact match or should we use embedding similarity for "similar tasks"?

3. **Judge agent selection**: Should adversarial test validation use a separate model (for objectivity) or can we reuse planner/reviewer?

4. **Test suite contamination**: How do we prevent adversarial tests from being committed to the actual test suite without review?

5. **Performance threshold calibration**: Should latency thresholds be task-specific or global? Different tasks have different acceptable runtimes.
