"""Artifact emission for deliberate runs."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from deliberate.config import DeliberateConfig
from deliberate.types import JuryResult
from deliberate.utils.hash_utils import hash_task


def _json_default(obj: Any) -> str:
    """Fallback serializer for JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, Enum):
        return obj.value
    return str(obj)


def _dataclass_to_dict(obj: Any) -> Any:
    """Convert dataclasses to dictionaries recursively."""
    if is_dataclass(obj):
        return {k: _dataclass_to_dict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [_dataclass_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    return obj


def write_run_artifact(
    result: JuryResult,
    output_dir: Path,
    profile_name: str | None = None,
    config: DeliberateConfig | None = None,
) -> Path:
    """Write the canonical run artifact."""
    output_dir.mkdir(parents=True, exist_ok=True)

    end_time = result.started_at + timedelta(seconds=result.total_duration_seconds)
    artifact = {
        "task": {
            "text": result.task,
            "hash": hash_task(result.task),
        },
        "profile": profile_name,
        "success": result.success,
        "summary": result.summary,
        "vote_result": {
            "winner_id": result.vote_result.winner_id if result.vote_result else None,
            "confidence": result.vote_result.confidence if result.vote_result else None,
            "scores": result.vote_result.scores if result.vote_result else None,
        },
        "metrics": {
            "duration_seconds": result.total_duration_seconds,
            "tokens": result.total_token_usage,
            "cost_usd": result.total_cost_usd,
        },
        "refinement": {
            "triggered": result.refinement_triggered,
            "iterations": len(result.refinement_iterations),
            "improvement_delta": result.final_improvement,
        },
        "timestamps": {
            "started_at": result.started_at,
            "ended_at": end_time,
        },
        "agents": {
            "planning": config.workflow.planning.agents if config else None,
            "execution": config.workflow.execution.agents if config else None,
            "review": config.workflow.review.agents if config else None,
        },
        "data": _dataclass_to_dict(result),
    }

    json_path = output_dir / "deliberate-run.json"
    json_path.write_text(json.dumps(artifact, indent=2, default=_json_default))
    return json_path


def write_markdown_report(
    result: JuryResult,
    output_dir: Path,
    profile_name: str | None = None,
    config: DeliberateConfig | None = None,
) -> Path:
    """Generate concise markdown report from result."""
    output_dir.mkdir(parents=True, exist_ok=True)
    confidence = result.vote_result.confidence if result.vote_result else 0.0
    verdict = "APPROVE" if result.success else "BLOCK"
    risk = "LOW" if result.success and confidence >= 0.6 else "MEDIUM"
    if not result.success:
        risk = "HIGH"

    refinement_summary = "none"
    if result.refinement_triggered:
        refinement_summary = (
            f"triggered ({len(result.refinement_iterations)} iteration(s), +{result.final_improvement:.2f} delta)"
        )

    key_issues: list[str] = []
    for review in result.reviews:
        if review.comments:
            key_issues.append(f"{review.reviewer}: {review.comments}")
        if len(key_issues) >= 5:
            break
    if not key_issues:
        key_issues.append("No explicit review issues captured.")

    models_used = []
    if config:
        if config.workflow.execution.agents:
            models_used.append(f"execution={','.join(config.workflow.execution.agents)}")
        if config.workflow.review.agents:
            models_used.append(f"review={','.join(config.workflow.review.agents)}")
        if config.workflow.planning.agents:
            models_used.append(f"planning={','.join(config.workflow.planning.agents)}")

    summary_lines = [
        "# deliberate report",
        "",
        "## Summary",
        f"- Verdict: {verdict}",
        f"- Overall risk: {risk}",
        f"- Confidence: {confidence:.2f}",
    ]
    if models_used:
        summary_lines.append(f"- Models: {'; '.join(models_used)}")
    summary_lines.append(f"- Refinement: {refinement_summary}")
    summary_lines.append(f"- Estimated cost: ${result.total_cost_usd:.2f}")
    summary_lines.append("")
    summary_lines.append("## Key issues")
    for idx, issue in enumerate(key_issues, start=1):
        summary_lines.append(f"{idx}. {issue}")
    summary_lines.append("")
    summary_lines.append("## Suggested follow-ups")
    summary_lines.append("- Add tests or linters if not present.")
    summary_lines.append("- Re-run with higher profile for more thorough coverage.")
    summary_lines.append("")
    summary_lines.append(f"_Generated by deliberate using profile `{profile_name or 'default'}`._")

    md_path = output_dir / "deliberate-report.md"
    md_path.write_text("\n".join(summary_lines))
    return md_path
