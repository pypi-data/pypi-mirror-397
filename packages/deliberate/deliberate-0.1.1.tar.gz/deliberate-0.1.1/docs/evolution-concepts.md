# Evolution Concepts in Deliberate

Deliberate incorporates ideas from two key research directions in AI-assisted software engineering: **AlphaEvolve** (Google DeepMind) and **Poetiq** (prompt engineering research).

## AlphaEvolve-Inspired Features

[AlphaEvolve](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) demonstrates how evolutionary algorithms combined with LLMs can discover novel solutions. Deliberate incorporates several key concepts:

### 1. MAP-Elites Program Database

The Program Database stores candidate solutions using a **MAP-elites** approach:

- **Quality-Diversity**: Rather than just tracking the "best" solution, we maintain diverse solutions that excel in different dimensions (correctness, speed, code quality)
- **Niche Competition**: Programs compete within behavioral niches, allowing multiple high-quality solutions to coexist
- **Elite Preservation**: Top performers in each niche are protected from replacement

```python
from deliberate.evolution import ProgramDatabase, DatabaseConfig

db = ProgramDatabase(config=DatabaseConfig(
    max_size=1000,
    island_count=4,
    elite_threshold=0.9,
))
```

### 2. Island-Based Populations

Inspired by island-model genetic algorithms:

- **Multiple Isolated Populations**: Each island evolves independently, exploring different solution spaces
- **Periodic Migration**: Champions migrate between islands to share good genes
- **Diversity Maintenance**: Island isolation prevents premature convergence

### 3. LLM Ensemble Strategy

AlphaEvolve uses different models for different purposes:

- **Fast Models** (Flash/Haiku): High throughput for exploring many variations
- **Powerful Models** (Pro/Opus): Quality improvements on promising candidates
- **Adaptive Selection**: Champions receive more powerful model attention

```yaml
# deliberate.yaml evolution config
workflow:
  evolution:
    enabled: true
    agents: [gemini-flash, claude-sonnet]  # Fast and powerful
    fast_model_ratio: 0.7  # 70% fast, 30% powerful
    use_powerful_for_champions: true
```

### 4. Diff-Based Evolution

Rather than generating complete code each iteration:

- **SEARCH/REPLACE Blocks**: Targeted modifications to specific code regions
- **Smaller Changes**: Diffs are more likely to preserve working functionality
- **Evolve Markers**: Optional `# EVOLVE-START` markers guide modifications

```python
# Example diff output from evolution
<<<<<<< SEARCH
def process(data):
    return data.strip()
=======
def process(data):
    return data.strip().lower()
>>>>>>> REPLACE
```

### 5. Evaluation Cascade

Progressive testing for early pruning:

1. **SYNTAX**: Fast syntax/lint check (catches obvious errors)
2. **UNIT_TESTS**: Run quick unit tests
3. **INTEGRATION**: Full integration test suite
4. **BENCHMARK**: Performance benchmarks (optional)

```python
from deliberate.evolution import EvaluationLevel

cascade_levels = [
    EvaluationLevel.SYNTAX,
    EvaluationLevel.UNIT_TESTS,
    EvaluationLevel.INTEGRATION,
]
```

### 6. Multi-Metric Optimization

Programs are scored on multiple dimensions:

- `correctness`: Test pass rate (0.0-1.0)
- `code_quality`: Lint score, complexity metrics
- `performance`: Benchmark results vs baseline
- `overall_score`: Weighted combination

## Poetiq-Inspired Features

Poetiq (Prompt-Oriented Engineering with Thoughtful Iterative Quality) emphasizes treating prompts as interfaces with structured feedback loops.

### 1. Iterative Feedback Loops

Deliberate's TDD loop embodies this philosophy:

1. **Run Tests**: Execute test suite
2. **Analyze Failures**: Parse error messages
3. **Generate Fix Prompt**: Include specific failure context
4. **Apply & Verify**: Test the fix immediately
5. **Repeat**: Until tests pass or max iterations

```python
# TDD loop in refinement phase
for iteration in range(max_iterations):
    result = await run_tests(worktree)
    if result.passed:
        break
    fix_prompt = build_fix_prompt(task, result.failures)
    await agent.fix(fix_prompt)
```

### 2. Self-Auditing Reviews

Multiple agents review each solution with structured criteria:

- **Correctness**: Does it solve the stated problem?
- **Code Quality**: Is it maintainable and idiomatic?
- **Completeness**: Are edge cases handled?
- **Risk**: Could this break existing functionality?

The review phase implements "self-auditing" by:
- Using different models than the implementers
- Aggregating votes using Borda count
- Requiring minimum confidence thresholds

### 3. Structured Feedback System

Deliberate provides structured feedback at every stage:

```python
# Example structured feedback from review
{
    "agent": "claude-reviewer",
    "scores": {
        "correctness": 8,
        "code_quality": 7,
        "completeness": 9,
        "risk": 3  # Lower is better for risk
    },
    "decision": "approve",
    "feedback": "Implementation is correct but could benefit from..."
}
```

### 4. Dynamic Criteria Generation

Before review, an LLM analyzes the task to generate relevant criteria:

```python
# Auto-generated criteria for a refactoring task
criteria = [
    "backward_compatibility",  # Does it maintain existing API?
    "performance_impact",      # Any slowdowns?
    "test_coverage",          # New tests for new code?
]
```

## Using Evolution in Deliberate

### Basic Usage

```bash
# Enable evolution with default settings
uv run deliberate run "Fix the bug in solver.py" --evolve

# Customize iteration count
uv run deliberate run "Optimize the parser" --evolve --evolve-iterations 20
```

### Configuration

```yaml
# .deliberate.yaml
workflow:
  evolution:
    enabled: true
    agents: [gemini-flash, claude-sonnet]
    max_iterations: 10
    target_score: 0.95
    fast_model_ratio: 0.7
    use_powerful_for_champions: true
    prefer_diffs: true
    max_stagnant_iterations: 5
    trigger_on_low_confidence: true
    min_confidence_threshold: 0.5
```

### Programmatic Usage

```python
from deliberate.evolution import (
    EvolutionController,
    ProgramDatabase,
    TDDEvaluator,
)

# Create components
database = ProgramDatabase()
evaluator = TDDEvaluator(working_dir=Path("./project"))

# Create controller
controller = EvolutionController(
    database=database,
    agents={"flash": flash_adapter, "pro": pro_adapter},
    evaluator=evaluator,
)

# Run evolution
result = await controller.evolve(
    task="Implement a sorting algorithm that's faster than O(n^2)",
    seed_program=initial_code,
)

print(f"Best solution: {result.best_program.code}")
print(f"Score: {result.best_program.metrics.overall_score}")
```

## When to Use Evolution

Evolution is most useful for:

1. **Complex algorithmic problems** where multiple valid solutions exist
2. **Optimization tasks** requiring iterative improvement
3. **Low-confidence results** from initial execution
4. **Test-driven scenarios** with clear pass/fail criteria

Evolution adds overhead, so skip it for:
- Simple, well-defined tasks
- High-confidence initial solutions
- Tasks without automated test validation

## References

- [AlphaEvolve: A Gemini-powered coding agent](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)
- [MAP-Elites: Illuminating search spaces](https://arxiv.org/abs/1504.04909)
- [SWE-Bench: Software Engineering Benchmark](https://www.swebench.com/)
