# Task: Fix Calculator Bugs

## Objective
Fix the bugs in `calculator.py` so that all tests pass.

## Current Issues
1. `divide(a, b)` crashes with ZeroDivisionError when b=0
2. `calculate(expression)` returns None for unknown operators instead of raising ValueError

## Success Criteria
- All tests in `test_calculator.py` pass
- Run tests with: `uv run pytest`

## Constraints
- Do not modify the test file
- Keep the existing function signatures
