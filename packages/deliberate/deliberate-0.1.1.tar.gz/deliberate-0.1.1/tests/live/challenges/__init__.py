"""Real software engineering challenges for testing deliberate.

These challenges are designed to test the evolution system with
problems that require:
1. Algorithmic thinking
2. Edge case handling
3. Performance optimization
4. Clean code practices
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SEChallenge:
    """A software engineering challenge for testing."""

    name: str
    description: str
    seed_code: str
    test_cases: dict[tuple, Any]
    function_name: str = "solve"
    difficulty: str = "medium"  # easy, medium, hard
    tags: list[str] = field(default_factory=list)

    def get_task_prompt(self) -> str:
        """Generate the task prompt for the LLM."""
        return f"""# {self.name}

{self.description}

## Function Signature

```python
def {self.function_name}(...):
    # Your implementation here
    pass
```

## Requirements

- Handle all edge cases
- Optimize for both correctness and performance
- Write clean, readable code
"""


# Challenge: Two Sum (Easy)
TWO_SUM = SEChallenge(
    name="Two Sum",
    description="""Given an array of integers `nums` and an integer `target`, return indices
of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may
not use the same element twice.

Example:
    nums = [2, 7, 11, 15], target = 9
    Output: [0, 1] (because nums[0] + nums[1] == 9)
""",
    seed_code="""def solve(nums: list[int], target: int) -> list[int]:
    # TODO: Implement two sum
    pass
""",
    # Use tuples as keys (hashable) - will convert to lists in evaluator
    test_cases={
        ((2, 7, 11, 15), 9): [0, 1],
        ((3, 2, 4), 6): [1, 2],
        ((3, 3), 6): [0, 1],
        ((-1, -2, -3, -4, -5), -8): [2, 4],
        ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 19): [8, 9],
    },
    function_name="solve",
    difficulty="easy",
    tags=["arrays", "hash-table", "interview"],
)

# Challenge: LRU Cache (Medium)
LRU_CACHE = SEChallenge(
    name="LRU Cache",
    description="""Design and implement a data structure for Least Recently Used (LRU) cache.

Implement the LRUCache class:
- `__init__(capacity: int)` Initialize the LRU cache with positive size capacity.
- `get(key: int) -> int` Return the value of the key if exists, otherwise -1.
- `put(key: int, value: int) -> None` Update or insert the value. When full,
  evict the least recently used key.

Both get and put must run in O(1) average time complexity.
""",
    seed_code="""class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        # TODO: Initialize data structures

    def get(self, key: int) -> int:
        # TODO: Get value and update recency
        pass

    def put(self, key: int, value: int) -> None:
        # TODO: Put value and handle capacity
        pass

def solve(operations: list[tuple]) -> list:
    \"\"\"Execute a sequence of operations and return results.

    Each operation is a tuple: ('get', key) or ('put', key, value)
    Returns list of results (get returns value, put returns None)
    \"\"\"
    results = []
    cache = None
    for op in operations:
        if op[0] == 'init':
            cache = LRUCache(op[1])
            results.append(None)
        elif op[0] == 'get':
            results.append(cache.get(op[1]))
        elif op[0] == 'put':
            cache.put(op[1], op[2])
            results.append(None)
    return results
""",
    # Use tuples as keys (hashable)
    test_cases={
        (
            (
                ("init", 2),
                ("put", 1, 1),
                ("put", 2, 2),
                ("get", 1),
                ("put", 3, 3),
                ("get", 2),
                ("put", 4, 4),
                ("get", 1),
                ("get", 3),
                ("get", 4),
            ),
        ): [None, None, None, 1, None, -1, None, -1, 3, 4],
        ((("init", 1), ("put", 2, 1), ("get", 2), ("put", 3, 2), ("get", 2), ("get", 3)),): [
            None,
            None,
            1,
            None,
            -1,
            2,
        ],
    },
    function_name="solve",
    difficulty="medium",
    tags=["design", "linked-list", "hash-table", "interview"],
)

# Challenge: Merge Intervals (Medium)
MERGE_INTERVALS = SEChallenge(
    name="Merge Intervals",
    description="""Given an array of intervals where intervals[i] = [start_i, end_i],
merge all overlapping intervals and return an array of non-overlapping intervals.

Example:
    Input: [[1,3],[2,6],[8,10],[15,18]]
    Output: [[1,6],[8,10],[15,18]]
    Explanation: [1,3] and [2,6] overlap, merged to [1,6]
""",
    seed_code="""def solve(intervals: list[list[int]]) -> list[list[int]]:
    # TODO: Merge overlapping intervals
    pass
""",
    # Use tuples as keys (hashable)
    test_cases={
        (((1, 3), (2, 6), (8, 10), (15, 18)),): [[1, 6], [8, 10], [15, 18]],
        (((1, 4), (4, 5)),): [[1, 5]],
        (((1, 4), (0, 4)),): [[0, 4]],
        (((1, 4), (2, 3)),): [[1, 4]],
        ((),): [],
        (((1, 4),),): [[1, 4]],
    },
    function_name="solve",
    difficulty="medium",
    tags=["arrays", "sorting", "interview"],
)

# Challenge: Word Search (Hard)
WORD_SEARCH = SEChallenge(
    name="Word Search",
    description="""Given an m x n grid of characters board and a string word, return true if
word exists in the grid.

The word can be constructed from letters of sequentially adjacent cells, where
adjacent cells are horizontally or vertically neighboring. The same letter cell
may not be used more than once.

Example:
    board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
    word = "ABCCED"
    Output: True
""",
    seed_code="""def solve(board: list[list[str]], word: str) -> bool:
    # TODO: Implement word search with backtracking
    pass
""",
    # Use tuples as keys (hashable)
    test_cases={
        ((("A", "B", "C", "E"), ("S", "F", "C", "S"), ("A", "D", "E", "E")), "ABCCED"): True,
        ((("A", "B", "C", "E"), ("S", "F", "C", "S"), ("A", "D", "E", "E")), "SEE"): True,
        ((("A", "B", "C", "E"), ("S", "F", "C", "S"), ("A", "D", "E", "E")), "ABCB"): False,
        ((("a",),), "a"): True,
        ((("a", "b"), ("c", "d")), "abcd"): False,
    },
    function_name="solve",
    difficulty="hard",
    tags=["backtracking", "matrix", "dfs", "interview"],
)

# Challenge: Serialize Binary Tree (Hard)
SERIALIZE_TREE = SEChallenge(
    name="Serialize and Deserialize Binary Tree",
    description="""Design an algorithm to serialize and deserialize a binary tree.

Serialization is converting a tree to a string. Deserialization is
reconstructing the tree from the string.

You must handle the case where the tree can be empty (None).

Implement:
- serialize(root) -> str: Encode tree to string
- deserialize(data) -> TreeNode: Decode string to tree
""",
    seed_code="""class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def serialize(root) -> str:
    # TODO: Implement serialization
    pass

def deserialize(data: str):
    # TODO: Implement deserialization
    pass

def solve(values: list) -> list:
    \"\"\"Test serialization/deserialization roundtrip.

    Input: List representing tree in level-order (None for missing nodes)
    Output: Same list after serialize -> deserialize roundtrip
    \"\"\"
    def build_tree(values):
        if not values or values[0] is None:
            return None
        root = TreeNode(values[0])
        queue = [root]
        i = 1
        while queue and i < len(values):
            node = queue.pop(0)
            if i < len(values) and values[i] is not None:
                node.left = TreeNode(values[i])
                queue.append(node.left)
            i += 1
            if i < len(values) and values[i] is not None:
                node.right = TreeNode(values[i])
                queue.append(node.right)
            i += 1
        return root

    def tree_to_list(root):
        if not root:
            return []
        result = []
        queue = [root]
        while queue:
            node = queue.pop(0)
            if node:
                result.append(node.val)
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append(None)
        # Remove trailing Nones
        while result and result[-1] is None:
            result.pop()
        return result

    tree = build_tree(values)
    serialized = serialize(tree)
    deserialized = deserialize(serialized)
    return tree_to_list(deserialized)
""",
    # Use tuples as keys (hashable)
    test_cases={
        ((1, 2, 3, None, None, 4, 5),): [1, 2, 3, None, None, 4, 5],
        ((),): [],
        ((1,),): [1],
        ((1, 2, 3, 4, 5, 6, 7),): [1, 2, 3, 4, 5, 6, 7],
    },
    function_name="solve",
    difficulty="hard",
    tags=["tree", "design", "bfs", "dfs", "interview"],
)

# All challenges
ALL_CHALLENGES = [
    TWO_SUM,
    MERGE_INTERVALS,
    LRU_CACHE,
    WORD_SEARCH,
    SERIALIZE_TREE,
]

# By difficulty
EASY_CHALLENGES = [c for c in ALL_CHALLENGES if c.difficulty == "easy"]
MEDIUM_CHALLENGES = [c for c in ALL_CHALLENGES if c.difficulty == "medium"]
HARD_CHALLENGES = [c for c in ALL_CHALLENGES if c.difficulty == "hard"]
