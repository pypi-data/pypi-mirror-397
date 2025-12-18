from pathlib import Path

from rich.console import Console

from deliberate.review_tui import ReviewTUI, resolve_editor_command
from deliberate.types import ExecutionResult


def test_resolve_editor_prefers_visual(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("VISUAL", "vim -u NONE")
    monkeypatch.delenv("EDITOR", raising=False)
    cmd = resolve_editor_command(tmp_path)
    assert cmd == ["vim", "-u", "NONE", str(tmp_path)]


def test_resolve_editor_falls_back_to_code(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr(
        "deliberate.review_tui.shutil.which",
        lambda name: "/usr/bin/code" if name == "code" else None,
    )
    cmd = resolve_editor_command(tmp_path)
    assert cmd == ["code", str(tmp_path)]


def test_open_worktree_uses_injected_launcher(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("VISUAL", "echo")
    calls: list[list[str]] = []

    def fake_launcher(cmd):
        calls.append(cmd)

        class _Proc: ...

        return _Proc()

    tui = ReviewTUI(Console(record=True))
    tui._editor_launcher = fake_launcher

    result = ExecutionResult(
        id="exec-test",
        agent="agent-a",
        worktree_path=tmp_path,
        diff=None,
        summary="",
        success=True,
    )

    tui._open_worktree(result)

    assert calls, "Editor launcher should have been invoked"
    assert calls[0][-1] == str(tmp_path)
