"""Evaluators for iterative solving.

Specialized SolutionEvaluator implementations for different domains:
- PlanReviewEvaluator: Evaluates plan quality using structure checks + LLM critic
"""

import re
from dataclasses import dataclass, field
from typing import Any

from deliberate.adapters.base import AdapterResponse, ModelAdapter
from deliberate.types import Plan

from .solver import SolutionEvaluator
from .types import FeedbackContext


@dataclass
class PlanStructureCheck:
    """Result of pre-LLM structure validation.

    Fast checks to catch malformed plans before expensive LLM critique.
    """

    valid: bool
    has_steps: bool = False
    has_risks: bool = False
    has_files: bool = False
    step_count: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def score(self) -> float:
        """Structure quality score (0.0-1.0)."""
        if not self.valid:
            return 0.0
        checks_passed = sum([self.has_steps, self.has_risks, self.has_files])
        base_score = checks_passed / 3.0
        # Bonus for having multiple steps
        if self.step_count >= 3:
            base_score = min(1.0, base_score + 0.1)
        return base_score


@dataclass
class CriticResult:
    """Result from LLM critic evaluation."""

    feasibility: float  # 0.0-1.0: Can this plan be implemented?
    completeness: float  # 0.0-1.0: Does it cover all requirements?
    clarity: float  # 0.0-1.0: Is it clear and unambiguous?
    risk_awareness: float  # 0.0-1.0: Are risks identified and mitigated?
    overall_score: float  # Weighted average
    feedback: str  # Critic's detailed feedback
    suggestions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CriticResult":
        """Create from parsed critic response."""
        return cls(
            feasibility=d.get("feasibility", 0.0),
            completeness=d.get("completeness", 0.0),
            clarity=d.get("clarity", 0.0),
            risk_awareness=d.get("risk_awareness", 0.0),
            overall_score=d.get("overall_score", 0.0),
            feedback=d.get("feedback", ""),
            suggestions=d.get("suggestions", []),
        )


class PlanReviewEvaluator(SolutionEvaluator[Plan]):
    """Evaluates plans using structure checks + LLM critic.

    Two-phase evaluation (per plan spec):
    1. Pre-LLM Structure Check: Fast validation that catches malformed plans
       - Has numbered steps?
       - Has risk section?
       - Has file list?
       Returns early with 0.0 score if basic structure is missing (saves tokens)

    2. LLM Critic: Scores plans on feasibility, completeness, risk, clarity
       Uses a cheap/fast model to evaluate plan quality.

    Success threshold: 0.9 (configurable)
    """

    def __init__(
        self,
        critic_agent: ModelAdapter | None = None,
        success_threshold: float = 0.9,
        require_structure: bool = True,
        weights: dict[str, float] | None = None,
    ):
        """Initialize the plan evaluator.

        Args:
            critic_agent: LLM for critic evaluation. If None, only structure check.
            success_threshold: Score threshold for success (default 0.9).
            require_structure: If True, fail immediately on bad structure.
            weights: Weights for critic criteria (default: equal).
        """
        self.critic_agent = critic_agent
        self.success_threshold = success_threshold
        self.require_structure = require_structure
        self.weights = weights or {
            "feasibility": 0.3,
            "completeness": 0.3,
            "clarity": 0.2,
            "risk_awareness": 0.2,
        }

    async def evaluate(self, solution: Plan, context: Any) -> tuple[FeedbackContext, dict[str, Any]]:
        """Evaluate a plan using structure check + LLM critic.

        Args:
            solution: The Plan to evaluate.
            context: Dict with optional 'task' (original task description).

        Returns:
            Tuple of (FeedbackContext, raw evaluation dict).
        """
        task = context.get("task", "") if isinstance(context, dict) else ""

        # Phase 1: Structure Check (fast, no LLM needed)
        structure = self._check_structure(solution.content)

        if self.require_structure and not structure.valid:
            # Early return - save tokens by not calling LLM
            feedback_ctx = FeedbackContext(
                expected="Well-structured plan with steps, risks, and files",
                actual=f"Plan missing required sections: {', '.join(structure.issues)}",
                match=False,
                soft_score=structure.score,
                errors=structure.issues,
            )
            raw_result = {
                "structure": structure,
                "critic": None,
                "passed": False,
                "score": structure.score,
            }
            return feedback_ctx, raw_result

        # Phase 2: LLM Critic (if agent available)
        critic_result = None
        if self.critic_agent:
            critic_result = await self._run_critic(solution.content, task)

        # Calculate final score
        if critic_result:
            final_score = critic_result.overall_score
            feedback_text = critic_result.feedback
            suggestions = critic_result.suggestions
        else:
            final_score = structure.score
            feedback_text = self._format_structure_feedback(structure)
            suggestions = []

        passed = final_score >= self.success_threshold

        feedback_ctx = FeedbackContext(
            expected=f"Plan score >= {self.success_threshold}",
            actual=f"Plan score: {final_score:.2f}",
            match=passed,
            soft_score=final_score,
            diff=feedback_text,
            errors=structure.issues if not passed else [],
            metadata={
                "structure_check": {
                    "has_steps": structure.has_steps,
                    "has_risks": structure.has_risks,
                    "has_files": structure.has_files,
                    "step_count": structure.step_count,
                },
                "critic_scores": {
                    "feasibility": critic_result.feasibility if critic_result else None,
                    "completeness": critic_result.completeness if critic_result else None,
                    "clarity": critic_result.clarity if critic_result else None,
                    "risk_awareness": critic_result.risk_awareness if critic_result else None,
                },
            },
        )

        raw_result = {
            "structure": structure,
            "critic": critic_result,
            "passed": passed,
            "score": final_score,
            "suggestions": suggestions,
        }

        return feedback_ctx, raw_result

    def is_success(self, feedback_context: FeedbackContext) -> bool:
        """Check if the plan passes the success threshold."""
        return feedback_context.soft_score >= self.success_threshold

    def _check_structure(self, plan_content: str) -> PlanStructureCheck:
        """Perform fast structure validation on plan content."""
        issues = []
        content_lower = plan_content.lower()

        # Check for numbered steps (1. 2. 3. or Step 1, Step 2, etc.)
        step_patterns = [
            r"^\s*\d+\.\s+",  # "1. Step"
            r"^\s*step\s+\d+",  # "Step 1"
            r"^\s*-\s+\[",  # "- [ ]" checkbox style
            r"^\s*\*\s+",  # "* item" bullet style
        ]
        steps_found = 0
        for line in plan_content.split("\n"):
            for pattern in step_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    steps_found += 1
                    break

        has_steps = steps_found >= 2  # At least 2 steps
        if not has_steps:
            issues.append("Missing numbered implementation steps (need at least 2)")

        # Check for risk section
        risk_keywords = ["risk", "concern", "potential issue", "caveat", "warning"]
        has_risks = any(kw in content_lower for kw in risk_keywords)
        if not has_risks:
            issues.append("Missing risk/concerns section")

        # Check for file list or affected files
        file_keywords = [
            "file",
            ".py",
            ".ts",
            ".js",
            ".tsx",
            ".jsx",
            ".rs",
            "src/",
            "tests/",
            "lib/",
        ]
        has_files = any(kw in content_lower for kw in file_keywords)
        if not has_files:
            issues.append("Missing affected files list")

        # Valid if has steps (minimum requirement)
        valid = has_steps

        return PlanStructureCheck(
            valid=valid,
            has_steps=has_steps,
            has_risks=has_risks,
            has_files=has_files,
            step_count=steps_found,
            issues=issues,
        )

    async def _run_critic(self, plan_content: str, task: str) -> CriticResult:
        """Run LLM critic to evaluate plan quality."""
        if not self.critic_agent:
            raise RuntimeError("_run_critic called without critic_agent")

        prompt = self._build_critic_prompt(plan_content, task)

        try:
            response: AdapterResponse = await self.critic_agent.call(prompt=prompt)
            return self._parse_critic_response(response.content)
        except Exception as e:
            # Return neutral scores on failure
            return CriticResult(
                feasibility=0.5,
                completeness=0.5,
                clarity=0.5,
                risk_awareness=0.5,
                overall_score=0.5,
                feedback=f"Critic evaluation failed: {e}",
                suggestions=[],
            )

    def _build_critic_prompt(self, plan_content: str, task: str) -> str:
        """Build the prompt for the critic LLM."""
        return f"""You are an expert software architect reviewing an implementation plan.

## Original Task
{task}

## Plan to Review
{plan_content}

## Evaluation Criteria
Evaluate the plan on these criteria (0.0 to 1.0 scale):

1. **Feasibility** (weight: {self.weights["feasibility"]:.0%})
   Can this plan be realistically implemented? Are the steps achievable?

2. **Completeness** (weight: {self.weights["completeness"]:.0%})
   Does the plan cover all aspects of the task? Are there gaps?

3. **Clarity** (weight: {self.weights["clarity"]:.0%})
   Is the plan clear and unambiguous? Can a developer follow it?

4. **Risk Awareness** (weight: {self.weights["risk_awareness"]:.0%})
   Are potential risks identified? Are mitigation strategies provided?

## Response Format
Respond with a JSON object:
```json
{{
  "feasibility": <0.0-1.0>,
  "completeness": <0.0-1.0>,
  "clarity": <0.0-1.0>,
  "risk_awareness": <0.0-1.0>,
  "overall_score": <weighted average>,
  "feedback": "<detailed feedback explaining scores>",
  "suggestions": ["<suggestion 1>", "<suggestion 2>", ...]
}}
```

Be rigorous but fair. A score of 0.9+ should indicate excellent quality."""

    def _parse_critic_response(self, response: str) -> CriticResult:
        """Parse the critic's JSON response."""
        import json

        # Try to extract JSON from response
        json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                # Calculate weighted overall if not provided
                if "overall_score" not in data:
                    data["overall_score"] = sum(data.get(k, 0.5) * w for k, w in self.weights.items())
                return CriticResult.from_dict(data)
            except json.JSONDecodeError:
                pass

        # Fallback: try to extract scores from text
        scores = {}
        for criterion in ["feasibility", "completeness", "clarity", "risk_awareness"]:
            match = re.search(rf"{criterion}[:\s]+(\d+\.?\d*)", response, re.IGNORECASE)
            if match:
                scores[criterion] = min(1.0, float(match.group(1)))
            else:
                scores[criterion] = 0.5  # Default

        overall = sum(scores.get(k, 0.5) * w for k, w in self.weights.items())

        return CriticResult(
            feasibility=scores.get("feasibility", 0.5),
            completeness=scores.get("completeness", 0.5),
            clarity=scores.get("clarity", 0.5),
            risk_awareness=scores.get("risk_awareness", 0.5),
            overall_score=overall,
            feedback=response[:500],  # Use response as feedback
            suggestions=[],
        )

    def _format_structure_feedback(self, structure: PlanStructureCheck) -> str:
        """Format structure check results as feedback text."""
        parts = []

        if structure.valid:
            parts.append("Plan structure is valid.")
            parts.append(f"- Found {structure.step_count} implementation steps")
            if structure.has_risks:
                parts.append("- Risk section present")
            if structure.has_files:
                parts.append("- File list present")
        else:
            parts.append("Plan structure is INVALID.")
            parts.append("\n## Issues:")
            for issue in structure.issues:
                parts.append(f"- {issue}")

        return "\n".join(parts)
