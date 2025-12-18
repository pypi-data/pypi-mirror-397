"""Ensure codex strategy injects MCP config flags."""

import json
from pathlib import Path

import pytest

from deliberate.adapters.cli_adapter import CLIAdapter, MCPServerConfig


@pytest.mark.asyncio
async def test_codex_injects_mcp_config(tmp_path: Path):
    # Create a mock codex CLI that captures arguments
    script = tmp_path / "codex-mock.sh"
    script_content = (
        "#!/usr/bin/env bash\n"
        "args=()\n"
        'for arg in "$@"; do\n'
        '  args+=("$arg")\n'
        "done\n"
        "# Output as JSON-like structure for parsing\n"
        'python3 -c \'import sys, json; print(json.dumps({"args": sys.argv[1:]}))\' "$@"\n'
    )
    script.write_text(script_content)
    script.chmod(0o755)

    adapter = CLIAdapter(
        name="codex-cli",
        command=[str(script)],
        timeout_seconds=5,
        mcp_servers=[
            MCPServerConfig(
                name="deliberate-orchestrator",
                command="dummy-mcp",
                args=["--url", "http://localhost:1234/sse"],
                env={"AUTH": "Bearer test-token"},
            )
        ],
    )

    response = await adapter.run_agentic(
        "noop task",
        working_dir=str(tmp_path),
        schema_name=None,
    )

    print(f"DEBUG: stdout: {response.stdout}")

    # The content should be the emitted mcp config JSON
    parsed = json.loads(response.content)
    args = parsed["args"]

    # Check for permission flags
    assert "--dangerously-bypass-approvals-and-sandbox" in args

    # Check for MCP config via -c
    config_flags = [a for i, a in enumerate(args) if i > 0 and args[i - 1] == "-c"]

    # We look for the presence of specific config settings
    assert any('mcp_servers.deliberate-orchestrator.command="dummy-mcp"' in f for f in config_flags)
    assert any(
        'mcp_servers.deliberate-orchestrator.args=["--url", "http://localhost:1234/sse"]' in f for f in config_flags
    )
    assert any('mcp_servers.deliberate-orchestrator.env={ AUTH="Bearer test-token" }' in f for f in config_flags)


@pytest.mark.asyncio
async def test_codex_skips_bypass_when_full_auto(tmp_path: Path):
    adapter = CLIAdapter(
        name="codex-cli",
        command=["codex", "--full-auto"],
    )

    flags = adapter._build_codex_permission_flags()

    assert flags == []
