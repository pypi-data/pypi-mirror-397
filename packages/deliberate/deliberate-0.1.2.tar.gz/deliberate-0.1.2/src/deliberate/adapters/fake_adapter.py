"""Fake adapter for testing without real API calls."""

import asyncio
import json
import random
import time
from dataclasses import dataclass, field
from typing import Callable

from deliberate.adapters.base import AdapterResponse, ModelAdapter


@dataclass
class FakeAdapter(ModelAdapter):
    """Fake adapter for testing without real API calls.

    Supports multiple behaviors:
    - echo: Returns the input prompt back
    - planner: Returns a structured plan
    - critic: Returns JSON review scores
    - flaky: Randomly fails based on fail_rate
    """

    name: str
    behavior: str = "echo"  # echo | planner | critic | flaky
    latency_seconds: float = 0.1
    fail_rate: float = 0.0
    _call_count: int = field(default=0, repr=False)

    async def call(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        working_dir: str | None = None,
        schema_name: str | None = None,
    ) -> AdapterResponse:
        """Make a fake completion call."""
        start = time.monotonic()
        self._call_count += 1

        await asyncio.sleep(self.latency_seconds)

        if self.behavior == "flaky" and random.random() < self.fail_rate:
            raise RuntimeError(f"[{self.name}] Simulated failure (call #{self._call_count})")

        content, raw_response = self._generate_response(prompt)

        return AdapterResponse(
            content=content,
            token_usage=self.estimate_tokens(prompt + content),
            duration_seconds=time.monotonic() - start,
            raw_response=raw_response,
            stdout=content,
        )

    async def run_agentic(
        self,
        task: str,
        *,
        working_dir: str,
        timeout_seconds: int = 1200,
        on_question: Callable[[str], str] | None = None,
        schema_name: str | None = None,
        extra_mcp_servers: list | None = None,
    ) -> AdapterResponse:
        """Simulate an agentic task execution."""
        start = time.monotonic()
        self._call_count += 1

        # Simulate longer execution time for agentic tasks
        await asyncio.sleep(self.latency_seconds * 5)

        if self.behavior == "flaky" and random.random() < self.fail_rate:
            raise RuntimeError(f"[{self.name}] Simulated agentic failure")

        content, raw_response = self._generate_agentic_response(task)

        return AdapterResponse(
            content=content,
            token_usage=self.estimate_tokens(task) * 3,
            duration_seconds=time.monotonic() - start,
            raw_response=raw_response,
            stdout=content,
        )

    def _generate_response(self, prompt: str) -> tuple[str, dict | None]:
        """Generate a response based on the configured behavior."""
        if self.behavior == "echo":
            return f"[{self.name}] Echo: {prompt[:200]}", None

        elif self.behavior == "planner":
            return (
                f"""## Plan from {self.name}

### Analysis
The task requires careful analysis of the existing codebase to identify components
that need modification.

### Approach
1. Review the current implementation and identify affected files
2. Design the solution with minimal changes
3. Implement changes incrementally with tests
4. Validate the changes work correctly

### Key Components
- Main logic module
- Test suite updates
- Documentation updates if needed

### Risks
- Potential breaking changes to existing APIs
- Need to ensure backward compatibility

### Estimated Complexity
Medium - requires careful implementation but straightforward approach.
""",
                None,
            )

        elif self.behavior == "judge":
            # Choose plan 1 by default via structured tool call
            return (
                "Selecting plan via tool.",
                {
                    "choices": [
                        {
                            "message": {
                                "tool_calls": [
                                    {
                                        "function": {
                                            "name": "select_plan",
                                            "arguments": json.dumps(
                                                {
                                                    "plan_id": 1,
                                                    "reasoning": f"{self.name} prefers the first plan.",
                                                }
                                            ),
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                },
            )

        elif self.behavior == "critic":
            review_payload = {
                "scores": {
                    "correctness": 8,
                    "code_quality": 7,
                    "completeness": 8,
                    "risk": 3,
                },
                "verdict": "accept",
                "reasoning": f"The solution addresses the core requirements effectively. "
                f"Analysis by {self.name}. Minor improvements possible in error handling.",
            }

            return (
                "Submitting review via tool.",
                {
                    "choices": [
                        {
                            "message": {
                                "tool_calls": [
                                    {
                                        "function": {
                                            "name": "submit_review",
                                            "arguments": json.dumps(review_payload),
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                },
            )

        elif self.behavior == "criteria":
            criteria = [
                {
                    "name": "Query Performance",
                    "description": "SQL plans minimize scans and avoid full table reads.",
                },
                {
                    "name": "Index Usage",
                    "description": "Indexes are used appropriately for filters and joins.",
                },
                {
                    "name": "Correctness",
                    "description": "Results remain accurate after optimization.",
                },
            ]
            return (
                "Setting review criteria.",
                {
                    "choices": [
                        {
                            "message": {
                                "tool_calls": [
                                    {
                                        "function": {
                                            "name": "set_review_criteria",
                                            "arguments": json.dumps({"criteria": criteria}),
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                },
            )

        elif self.behavior == "flaky":
            return f"[{self.name}] Flaky response (succeeded this time)", None

        return f"[{self.name}] Unknown behavior: {self.behavior}", None

    def _generate_agentic_response(self, task: str) -> tuple[str, dict | None]:
        """Generate an agentic execution response."""
        return (
            f"""## Execution Complete

### Task
{task[:150]}...

### Changes Made
Modified 2 files:
- `src/main.py`: Added new function implementing the requested feature
- `tests/test_main.py`: Added comprehensive tests

### Summary
Successfully implemented the requested changes. All tests pass.

### Diff
```diff
--- a/src/main.py
+++ b/src/main.py
@@ -1,5 +1,12 @@
 def existing_function():
     \"\"\"Existing function.\"\"\"
     pass
+
+
+def new_function():
+    \"\"\"New function added by {self.name}.\"\"\"
+    return "implemented"
```

### Test Results
All 5 tests passed.
""",
            None,
        )

    @property
    def call_count(self) -> int:
        """Get the number of calls made to this adapter."""
        return self._call_count

    def reset_call_count(self) -> None:
        """Reset the call counter."""
        self._call_count = 0
