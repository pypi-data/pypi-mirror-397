"""Tests for the data processing pipeline.

Includes both functional tests and performance tests.
Performance tests have strict time limits.
"""

import random
import time

import pytest
from data_pipeline import (
    find_duplicates,
    find_top_k,
    group_by_key,
    merge_sorted_lists,
)


class TestFindDuplicates:
    """Functional tests for find_duplicates."""

    def test_empty_list(self):
        assert find_duplicates([]) == []

    def test_no_duplicates(self):
        assert find_duplicates([1, 2, 3, 4, 5]) == []

    def test_with_duplicates(self):
        result = find_duplicates([1, 2, 3, 2, 1, 4, 1])
        assert result == [1, 2]

    def test_all_duplicates(self):
        result = find_duplicates([1, 1, 1])
        assert result == [1]


class TestMergeSortedLists:
    """Functional tests for merge_sorted_lists."""

    def test_empty_lists(self):
        assert merge_sorted_lists([], []) == []

    def test_one_empty(self):
        assert merge_sorted_lists([1, 2, 3], []) == [1, 2, 3]
        assert merge_sorted_lists([], [4, 5, 6]) == [4, 5, 6]

    def test_merge(self):
        result = merge_sorted_lists([1, 3, 5], [2, 4, 6])
        assert result == [1, 2, 3, 4, 5, 6]


class TestFindTopK:
    """Functional tests for find_top_k."""

    def test_basic(self):
        result = find_top_k([3, 1, 4, 1, 5, 9, 2, 6], 3)
        assert result == [9, 6, 5]

    def test_with_key(self):
        items = [{"score": 10}, {"score": 5}, {"score": 15}]
        result = find_top_k(items, 2, key=lambda x: x["score"])
        assert result == [{"score": 15}, {"score": 10}]


class TestGroupByKey:
    """Functional tests for group_by_key."""

    def test_basic(self):
        result = group_by_key(["apple", "banana", "apricot"], lambda x: x[0])
        assert result == {"a": ["apple", "apricot"], "b": ["banana"]}

    def test_empty(self):
        assert group_by_key([], lambda x: x) == {}


# Performance tests - these have strict time limits
class TestPerformance:
    """Performance tests with strict time limits."""

    @pytest.mark.performance
    def test_find_duplicates_performance(self):
        """find_duplicates should handle 100k items in < 100ms."""
        # Generate data with some duplicates
        items = list(range(90000)) + list(range(10000))
        random.shuffle(items)

        start = time.perf_counter()
        result = find_duplicates(items)
        elapsed = time.perf_counter() - start

        # Verify correctness
        assert len(result) == 10000
        assert all(items.count(x) > 1 for x in result)

        # Verify performance
        assert elapsed < 0.1, f"find_duplicates took {elapsed:.3f}s, limit is 0.1s"

    @pytest.mark.performance
    def test_merge_sorted_performance(self):
        """merge_sorted_lists should handle 50k+50k items in < 50ms."""
        list1 = sorted(random.sample(range(200000), 50000))
        list2 = sorted(random.sample(range(200000), 50000))

        start = time.perf_counter()
        result = merge_sorted_lists(list1, list2)
        elapsed = time.perf_counter() - start

        # Verify correctness
        assert len(result) == 100000
        assert result == sorted(result)

        # Verify performance
        assert elapsed < 0.05, f"merge_sorted_lists took {elapsed:.3f}s, limit is 0.05s"

    @pytest.mark.performance
    def test_find_top_k_performance(self):
        """find_top_k should handle 100k items, k=10 in < 50ms."""
        items = list(range(100000))
        random.shuffle(items)

        start = time.perf_counter()
        result = find_top_k(items, 10)
        elapsed = time.perf_counter() - start

        # Verify correctness
        assert result == list(range(99999, 99989, -1))

        # Verify performance
        assert elapsed < 0.05, f"find_top_k took {elapsed:.3f}s, limit is 0.05s"

    @pytest.mark.performance
    def test_group_by_key_performance(self):
        """group_by_key should handle 50k items in < 100ms."""
        items = [f"item_{i % 100}_{i}" for i in range(50000)]

        start = time.perf_counter()
        result = group_by_key(items, lambda x: x.split("_")[1])
        elapsed = time.perf_counter() - start

        # Verify correctness
        assert len(result) == 100
        assert all(len(v) == 500 for v in result.values())

        # Verify performance
        assert elapsed < 0.1, f"group_by_key took {elapsed:.3f}s, limit is 0.1s"
