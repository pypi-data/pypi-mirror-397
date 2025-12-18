"""Data processing pipeline - NEEDS OPTIMIZATION.

All functions produce correct output but are too slow.
Optimize without changing the function signatures or return formats.
"""

from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")


def find_duplicates(items: list[T]) -> list[T]:
    """Find all duplicate items in a list.

    Args:
        items: List of items (may contain duplicates)

    Returns:
        List of items that appear more than once, in order of first occurrence

    Example:
        >>> find_duplicates([1, 2, 3, 2, 1, 4, 1])
        [1, 2]
    """
    # SLOW: O(n²) implementation
    duplicates = []
    for i, item in enumerate(items):
        if item in duplicates:
            continue
        count = 0
        for other in items:
            if other == item:
                count += 1
        if count > 1:
            duplicates.append(item)
    return duplicates


def merge_sorted_lists(list1: list[T], list2: list[T]) -> list[T]:
    """Merge two sorted lists into a single sorted list.

    Args:
        list1: First sorted list
        list2: Second sorted list

    Returns:
        Merged sorted list

    Example:
        >>> merge_sorted_lists([1, 3, 5], [2, 4, 6])
        [1, 2, 3, 4, 5, 6]
    """
    # SLOW: Creates many intermediate lists
    result = []
    l1 = list(list1)  # Copy
    l2 = list(list2)  # Copy

    while l1 and l2:
        if l1[0] <= l2[0]:
            result = result + [l1[0]]  # Creates new list each time!
            l1 = l1[1:]  # Creates new list each time!
        else:
            result = result + [l2[0]]
            l2 = l2[1:]

    result = result + l1 + l2
    return result


def find_top_k(
    items: list[T],
    k: int,
    key: Callable[[T], Any] | None = None,
) -> list[T]:
    """Find the top k items by value (or by key function).

    Args:
        items: List of items
        k: Number of top items to return
        key: Optional key function for comparison

    Returns:
        List of top k items in descending order

    Example:
        >>> find_top_k([3, 1, 4, 1, 5, 9, 2, 6], 3)
        [9, 6, 5]
    """
    # SLOW: Sorts entire list when we only need k items
    if key is None:

        def key(x):
            return x

    # Full sort - O(n log n) when O(n log k) is possible
    sorted_items = sorted(items, key=key, reverse=True)
    return sorted_items[:k]


def group_by_key(
    items: Iterable[T],
    key_func: Callable[[T], Any],
) -> dict[Any, list[T]]:
    """Group items by a key function.

    Args:
        items: Iterable of items to group
        key_func: Function to extract grouping key from each item

    Returns:
        Dictionary mapping keys to lists of items with that key

    Example:
        >>> group_by_key(['apple', 'banana', 'apricot'], lambda x: x[0])
        {'a': ['apple', 'apricot'], 'b': ['banana']}
    """
    # SLOW: Inefficient nested loop approach
    items_list = list(items)

    # First, find all unique keys (inefficiently)
    keys = []
    for item in items_list:
        k = key_func(item)
        found = False
        for existing in keys:
            if existing == k:
                found = True
                break
        if not found:
            keys.append(k)

    # Then, build groups (another full pass for each key!)
    result = {}
    for k in keys:
        result[k] = []
        for item in items_list:
            if key_func(item) == k:
                result[k].append(item)

    return result


def process_pipeline(
    data: list[dict[str, Any]],
    filters: list[Callable[[dict], bool]],
    transforms: list[Callable[[dict], dict]],
) -> list[dict[str, Any]]:
    """Process data through a pipeline of filters and transforms.

    Args:
        data: List of data records
        filters: List of filter functions (keep items where filter returns True)
        transforms: List of transform functions to apply in sequence

    Returns:
        Filtered and transformed data
    """
    # This one is actually reasonably efficient
    result = []
    for record in data:
        # Apply filters
        passes_all = True
        for f in filters:
            if not f(record):
                passes_all = False
                break
        if not passes_all:
            continue

        # Apply transforms
        transformed = record.copy()
        for t in transforms:
            transformed = t(transformed)
        result.append(transformed)

    return result
