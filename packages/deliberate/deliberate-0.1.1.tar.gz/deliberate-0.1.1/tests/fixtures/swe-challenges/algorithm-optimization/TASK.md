# Task: Optimize Data Processing Pipeline

## Objective
Optimize the slow data processing functions in `data_pipeline.py` to meet performance requirements.

## Current Problems
The code works correctly but is too slow:
1. `find_duplicates()` is O(n²) - needs to be O(n) or O(n log n)
2. `merge_sorted_lists()` creates unnecessary intermediate lists
3. `find_top_k()` sorts the entire list when it doesn't need to
4. `group_by_key()` uses inefficient nested loops

## Requirements
1. All functions must produce the same output as before
2. All tests must pass within the time limits
3. Memory usage should not significantly increase

## Performance Targets
- `find_duplicates`: < 100ms for 100,000 items
- `merge_sorted_lists`: < 50ms for two 50,000-item lists
- `find_top_k`: < 50ms for 100,000 items, k=10
- `group_by_key`: < 100ms for 50,000 items

## Success Criteria
- All 8 functional tests pass
- All 4 performance tests pass (marked with `@pytest.mark.performance`)
- Total test suite runs in < 5 seconds

## Hints
- Consider using sets for duplicate detection
- Use heapq for top-k problems
- Consider generator expressions to avoid intermediate lists
- defaultdict can help with grouping
