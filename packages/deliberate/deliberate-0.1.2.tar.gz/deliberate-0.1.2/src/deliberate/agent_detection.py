"""Agent detection and MCP server discovery for deliberate init."""

import asyncio
import json
import os
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict


class AgentProbe(TypedDict):
    """Type definition for agent probe configuration."""

    name: str
    detect_cmd: list[str]
    auth_test_cmd: list[str]
    command: list[str]
    capabilities: list[str]
    timeout: int
    mcp_config_paths: list[Path]


@dataclass
class MCPServer:
    """MCP server configuration."""

    name: str
    command: str | list[str]
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    source: str = ""  # where we found this (e.g., "claude_desktop_config.json")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for YAML serialization."""
        result: dict[str, Any] = {"command": self.command}
        if self.args:
            result["args"] = self.args
        if self.env:
            result["env"] = self.env
        return result


@dataclass
class DetectedAgent:
    """A detected LLM agent with auth status."""

    name: str
    command: list[str]
    capabilities: list[str]
    authenticated: bool
    auth_error: str | None = None
    version: str | None = None
    mcp_servers: list[MCPServer] = field(default_factory=list)

    @property
    def has_auth(self) -> bool:
        """Check if agent is authenticated."""
        return self.authenticated and not self.auth_error


# Agent probe configurations
# TODO use pathlib for joining paths to support other operating systems
AGENT_PROBES: list[AgentProbe] = [
    {
        "name": "claude",
        "detect_cmd": ["claude", "--version"],
        "auth_test_cmd": ["claude", "--print", "-p", "Say 'ok'"],
        "command": ["claude"],
        "capabilities": ["planner", "executor", "reviewer"],
        "timeout": 30,
        "mcp_config_paths": [
            Path.home() / ".claude" / "claude_desktop_config.json",
            Path.home() / ".config" / "Claude" / "claude_desktop_config.json",
            Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        ],
    },
    {
        "name": "gemini",
        "detect_cmd": ["gemini", "--version"],
        "auth_test_cmd": ["gemini", "-y", "Say 'ok'"],
        "command": ["gemini", "-y", "--output-format", "json"],
        "capabilities": ["planner", "executor", "reviewer"],
        "timeout": 30,
        "mcp_config_paths": [],  # TODO: Find gemini MCP config path
    },
    {
        "name": "openai",
        "detect_cmd": ["openai", "--version"],
        "auth_test_cmd": [
            "openai",
            "api",
            "chat.completions.create",
            "-m",
            "gpt-4o-mini",
            "-g",
            "user",
            "Say 'ok'",
        ],
        "command": ["openai", "api", "chat.completions.create"],
        "capabilities": ["planner", "executor", "reviewer"],
        "timeout": 30,
        "mcp_config_paths": [],
    },
    {
        "name": "codex",
        "detect_cmd": ["codex", "--version"],
        "auth_test_cmd": ["codex", "exec", "--skip-git-repo-check", "Say 'ok'"],
        "command": ["codex", "exec", "--skip-git-repo-check"],
        "capabilities": ["planner", "executor", "reviewer"],
        "timeout": 30,
        "mcp_config_paths": [],
    },
    {
        "name": "aider",
        "detect_cmd": ["aider", "--version"],
        "auth_test_cmd": ["aider", "--message", "Say 'ok'", "--yes", "--no-git"],
        "command": ["aider", "--yes"],
        "capabilities": ["executor"],
        "timeout": 30,
        "mcp_config_paths": [],  # aider doesn't use MCP
    },
    {
        "name": "copilot",
        "detect_cmd": ["gh", "copilot", "--version"],
        "auth_test_cmd": ["gh", "copilot", "explain", "echo hello"],
        "command": ["gh", "copilot", "suggest"],
        "capabilities": ["planner", "executor"],
        "timeout": 30,
        "mcp_config_paths": [],
    },
    {
        "name": "cursor",
        "detect_cmd": ["cursor", "--version"],
        "auth_test_cmd": ["cursor", "chat", "Say 'ok'"],
        "command": ["cursor", "chat"],
        "capabilities": ["planner", "executor", "reviewer"],
        "timeout": 30,
        "mcp_config_paths": [],
    },
]


async def _run_command(
    cmd: list[str],
    timeout: int = 5,
    check_output: bool = True,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    # Prepare environment: inherit current env, apply overrides, and set CI/BROWSER to suppress interactivity
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    # Force non-interactive mode for most tools
    full_env.update(
        {
            "CI": "true",  # Tells many tools (gh, etc) to be non-interactive
            "BROWSER": "false",  # Prevents opening a web browser
            "DEBIAN_FRONTEND": "noninteractive",
        }
    )

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.DEVNULL,  # Prevent tools from waiting on user input
            env=full_env,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout,
        )
        return (
            proc.returncode or 0,
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return (-1, "", "Command timed out")
    except Exception as e:
        return (-1, "", str(e))


async def _load_mcp_servers_from_claude_cli() -> list[MCPServer]:
    """Load MCP servers from claude mcp list command."""
    try:
        returncode, stdout, stderr = await _run_command(
            ["claude", "mcp", "list"],
            timeout=10,
        )

        if returncode != 0:
            return []

        servers = []
        # Parse output like: "playwright: npx @playwright/mcp@latest - ✓ Connected"
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line or "Checking MCP server health" in line:
                continue

            # Extract name and command
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    rest = parts[1].strip()

                    # Extract command (before the status indicator)
                    if " - ✓" in rest or " - ✗" in rest:
                        command_part = rest.split(" - ")[0].strip()
                    else:
                        command_part = rest

                    # Parse command
                    if command_part.startswith("http"):
                        # HTTP/SSE server
                        command = command_part.split()[0]
                        args = []
                    else:
                        # stdio server (e.g., "npx @playwright/mcp@latest")
                        cmd_parts = command_part.split()
                        command = cmd_parts[0] if cmd_parts else command_part
                        args = cmd_parts[1:] if len(cmd_parts) > 1 else []

                    servers.append(
                        MCPServer(
                            name=name,
                            command=command,
                            args=args,
                            env={},
                            source="claude mcp list",
                        )
                    )

        return servers
    except Exception:
        return []


async def _load_mcp_servers_from_gemini_cli() -> list[MCPServer]:
    """Load MCP servers from gemini mcp list command."""
    try:
        returncode, stdout, stderr = await _run_command(
            ["gemini", "mcp", "list"],
            timeout=10,
        )

        if returncode != 0:
            return []

        servers = []
        # Parse output like: "✓ playwright: npx @playwright/mcp@latest (stdio) - Connected"
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line or "Configured MCP servers" in line:
                continue

            # Remove ANSI color codes
            import re

            line = re.sub(r"\x1b\[[0-9;]*m", "", line)

            # Remove status indicator at start (✓ or ✗)
            line = re.sub(r"^[✓✗]\s*", "", line)

            # Extract name and command
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    rest = parts[1].strip()

                    # Extract command (before the transport type in parentheses)
                    # e.g., "npx @playwright/mcp@latest (stdio) - Connected"
                    if "(" in rest:
                        command_part = rest.split("(")[0].strip()
                    else:
                        command_part = rest.split(" - ")[0].strip() if " - " in rest else rest

                    # Parse command
                    if command_part.startswith("http"):
                        # HTTP/SSE server
                        command = command_part.split()[0]
                        args = []
                    else:
                        # stdio server (e.g., "npx @playwright/mcp@latest")
                        cmd_parts = command_part.split()
                        command = cmd_parts[0] if cmd_parts else command_part
                        args = cmd_parts[1:] if len(cmd_parts) > 1 else []

                    servers.append(
                        MCPServer(
                            name=name,
                            command=command,
                            args=args,
                            env={},
                            source="gemini mcp list",
                        )
                    )

        return servers
    except Exception:
        return []


async def _load_mcp_servers_from_codex_cli() -> list[MCPServer]:
    """Load MCP servers from codex mcp list command."""
    try:
        returncode, stdout, stderr = await _run_command(
            ["codex", "mcp", "list"],
            timeout=10,
        )

        if returncode != 0:
            return []

        servers = []
        lines = stdout.strip().split("\n")

        # Codex outputs tables with headers. Parse based on the header row.
        # Table 1: stdio servers - "Name    Command     Args ..."
        # Table 2: HTTP servers - "Name    Url ..."

        parsing_stdio = False
        parsing_http = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect table type by header
            if line.startswith("Name") and "Command" in line and "Args" in line:
                parsing_stdio = True
                parsing_http = False
                continue
            elif line.startswith("Name") and "Url" in line:
                parsing_stdio = False
                parsing_http = True
                continue

            # Skip header separator lines
            if all(c in " -" for c in line):
                continue

            # Parse stdio server table rows
            if parsing_stdio:
                # Format: "Name    Command     Args ... Env ... Cwd  Status   Auth"
                parts = line.split(None, 2)  # Split on whitespace, max 3 parts
                if len(parts) >= 2:
                    name = parts[0].strip()
                    command = parts[1].strip()

                    # Try to extract args (before "Env" column)
                    args = []
                    if len(parts) >= 3:
                        rest = parts[2]
                        # Args are between command and "Env" or other columns
                        # Look for common patterns
                        arg_part = rest.split("  ")[0].strip()  # First continuous text
                        if arg_part and not arg_part.startswith("GITLAB_") and arg_part != "-":
                            args = arg_part.split()

                    servers.append(
                        MCPServer(
                            name=name,
                            command=command,
                            args=args,
                            env={},
                            source="codex mcp list",
                        )
                    )

            # Parse HTTP server table rows
            elif parsing_http:
                # Format: "Name    Url ... Status   Auth"
                parts = line.split(None, 1)  # Split into name and rest
                if len(parts) >= 2:
                    name = parts[0].strip()
                    # Extract URL (first continuous text after name)
                    url_part = parts[1].split()[0].strip()

                    if url_part.startswith("http"):
                        servers.append(
                            MCPServer(
                                name=name,
                                command=url_part,
                                args=[],
                                env={},
                                source="codex mcp list",
                            )
                        )

        return servers
    except Exception:
        return []


def _load_mcp_servers_from_claude_config(config_path: Path) -> list[MCPServer]:
    """Load MCP servers from Claude Desktop config file (fallback)."""
    if not config_path.exists():
        return []

    try:
        config = json.loads(config_path.read_text())
        mcp_config = config.get("mcpServers", {})
        servers = []

        for name, server_config in mcp_config.items():
            command = server_config.get("command")
            if not command:
                continue

            args = server_config.get("args", [])
            env = server_config.get("env", {})

            servers.append(
                MCPServer(
                    name=name,
                    command=command,
                    args=args,
                    env=env,
                    source=config_path.name,
                )
            )

        return servers
    except Exception:
        return []


async def _detect_mcp_servers_for_agent(probe: AgentProbe) -> list[MCPServer]:
    """Detect MCP servers configured for an agent."""
    servers = []

    # Try CLI commands first (preferred method)
    if probe["name"] == "claude":
        servers = await _load_mcp_servers_from_claude_cli()
        if servers:
            return servers

        # Fallback to config files
        for config_path in probe.get("mcp_config_paths", []):
            servers.extend(_load_mcp_servers_from_claude_config(config_path))

    elif probe["name"] == "gemini":
        servers = await _load_mcp_servers_from_gemini_cli()
        if servers:
            return servers

    elif probe["name"] == "codex":
        servers = await _load_mcp_servers_from_codex_cli()
        if servers:
            return servers

    # Add other agent-specific MCP config loaders here

    return servers


async def detect_agents(
    skip_auth_check: bool = False,
    skip_mcp_detection: bool = False,
    verbose: bool = False,
    progress_callback: Callable[[str], None] | None = None,
) -> list[DetectedAgent]:
    """Detect installed CLI tools and check authentication.

    Args:
        skip_auth_check: Skip authentication verification (faster)
        skip_mcp_detection: Skip MCP server detection (faster)
        verbose: Print verbose output during detection
        progress_callback: Optional callback(message: str) for progress updates

    Returns:
        List of detected agents with their configuration
    """
    detected = []

    for probe in AGENT_PROBES:
        if progress_callback:
            progress_callback(f"Checking for {probe['name']}...")
        # Check if binary exists
        binary = shutil.which(probe["detect_cmd"][0])
        if not binary:
            if progress_callback:
                progress_callback(f"  {probe['name']}: not found")
            continue

        if progress_callback:
            progress_callback(f"  {probe['name']}: found at {binary}")

        # Get version
        version = None
        try:
            returncode, stdout, stderr = await _run_command(
                probe["detect_cmd"],
                timeout=5,
            )
            if returncode == 0:
                # Extract first line of version output
                version = stdout.strip().split("\n")[0][:50]
                if progress_callback:
                    progress_callback(f"  {probe['name']}: version {version}")
        except Exception:
            pass

        # Auth check (costs ~10 tokens, ~$0.0001)
        authenticated = False
        auth_error = None

        if not skip_auth_check:
            if progress_callback:
                progress_callback(f"  {probe['name']}: checking authentication...")

            returncode, stdout, stderr = await _run_command(
                probe["auth_test_cmd"],
                timeout=probe["timeout"],
            )

            if returncode == 0:
                authenticated = True
                if progress_callback:
                    progress_callback(f"  {probe['name']}: authenticated ✓")
            else:
                # Capture first line of error
                auth_error = stderr.strip().split("\n")[0][:200] if stderr.strip() else "Authentication check failed"
                if progress_callback:
                    progress_callback(f"  {probe['name']}: auth failed ✗")

        # Detect MCP servers (can be slow - involves running CLI commands)
        mcp_servers: list[MCPServer] = []
        if not skip_mcp_detection:
            if progress_callback:
                progress_callback(f"  {probe['name']}: checking MCP servers...")
            mcp_servers = await _detect_mcp_servers_for_agent(probe)
            if progress_callback and mcp_servers:
                progress_callback(f"  {probe['name']}: found {len(mcp_servers)} MCP server(s)")

        detected.append(
            DetectedAgent(
                name=probe["name"],
                command=probe["command"],
                capabilities=probe["capabilities"],
                authenticated=authenticated or skip_auth_check,
                auth_error=auth_error,
                version=version,
                mcp_servers=mcp_servers,
            )
        )

    return detected


def generate_config(
    agents: list[DetectedAgent],
    selected_mcp_servers: dict[str, dict[str, list[str]]] | None = None,
    default_profile: str = "balanced",
) -> str:
    """Generate YAML config from detected agents.

    Args:
        agents: List of detected agents to include
        selected_mcp_servers: Dict of {agent_name: {phase: [server_names]}}
                             E.g., {"claude": {"planning": ["filesystem"], "execution": []}}
        default_profile: Default profile to use (cheap, balanced, powerful)

    Returns:
        YAML configuration string
    """
    authenticated = [a for a in agents if a.has_auth]

    if not authenticated:
        # Fall back to fake agent for testing
        return _generate_fallback_config()

    lines = [
        "# deliberate configuration",
        "# Auto-generated by 'deliberate init'",
        "",
        "agents:",
    ]

    # Add authenticated agents
    for agent in authenticated:
        lines.append(f"  {agent.name}:")
        lines.append("    type: cli")
        lines.append(f"    command: {agent.command}")
        lines.append(f"    parser: {agent.name}")

        # Add default models
        if agent.name == "claude":
            lines.append("    model: claude-sonnet-4-5-20250929")
        elif agent.name == "gemini":
            lines.append("    model: gemini-2.0-flash-exp")
        elif agent.name == "codex":
            lines.append("    model: gpt-5.1-codex-mini")

        lines.append(f"    capabilities: {agent.capabilities}")

        # Add agent-specific config
        if agent.name == "claude":
            lines.append("    permission_mode: bypassPermissions  # Allow headless file operations")
            lines.append("    config:")
            lines.append("      max_tokens: 16000")
            lines.append("      timeout_seconds: 1200")
        elif agent.name == "codex":
            lines.append("    config:")
            lines.append("      max_tokens: 16000")
            lines.append("      timeout_seconds: 1200")
        elif agent.name == "gemini":
            lines.append("    config:")
            lines.append("      max_tokens: 16000")
            lines.append("      timeout_seconds: 1200")

        # Add MCP servers if configured
        if selected_mcp_servers and agent.name in selected_mcp_servers:
            agent_mcp = selected_mcp_servers[agent.name]
            if any(servers for servers in agent_mcp.values()):
                lines.append("    mcp_servers:")
                for phase, server_names in agent_mcp.items():
                    if server_names:
                        lines.append(f"      {phase}:")
                        for server_name in server_names:
                            # Find the server config
                            server = next(
                                (s for s in agent.mcp_servers if s.name == server_name),
                                None,
                            )
                            if server:
                                lines.append(f"        {server_name}:")
                                server_dict = server.to_dict()
                                for key, value in server_dict.items():
                                    if isinstance(value, list):
                                        lines.append(f"          {key}:")
                                        for item in value:
                                            lines.append(f"            - {item}")
                                    elif isinstance(value, dict):
                                        lines.append(f"          {key}:")
                                        for k, v in value.items():
                                            lines.append(f"            {k}: {v}")
                                    else:
                                        lines.append(f"          {key}: {value}")

        lines.append("")

    # Add fake agent for testing
    lines.extend(
        [
            "  # Fake agent for testing (no API calls)",
            "  fake:",
            "    type: fake",
            "    behavior: planner",
            "    capabilities: [planner, executor, reviewer]",
            "",
        ]
    )

    # Workflow using first authenticated agent
    primary = authenticated[0].name
    reviewers = [a.name for a in authenticated if "reviewer" in a.capabilities]

    lines.extend(
        [
            "workflow:",
            "  planning:",
            "    enabled: true",
            f"    agents: [{primary}]",
            "",
            "  execution:",
            "    enabled: true",
            f"    agents: [{primary}]",
            "    worktree:",
            "      enabled: true",
            "      root: .deliberate/worktrees",
            "      cleanup: true",
            "",
            "  review:",
            f"    enabled: {str(len(reviewers) > 1).lower()}",
            f"    agents: [{', '.join(reviewers[:3])}]" if reviewers else "    agents: []",
            "",
            "limits:",
            "  budget:",
            "    max_total_tokens: 500000",
            "    max_cost_usd: 10.0",
            "    max_requests_per_agent: 30",
            "  time:",
            "    hard_timeout_minutes: 45",
            "",
            f"default_profile: {default_profile}",
            "",
            "# Available profiles: cheap, balanced, powerful",
            "# Run with --profile <name> to override, e.g.:",
            "#   deliberate run 'task' --profile cheap",
        ]
    )

    return "\n".join(lines)


def _generate_fallback_config() -> str:
    """Generate a fallback config when no agents are authenticated."""
    return """# deliberate configuration
# No authenticated agents found - using fake agent for testing

agents:
  fake:
    type: fake
    behavior: planner
    capabilities: [planner, executor, reviewer]

workflow:
  planning:
    enabled: true
    agents: [fake]

  execution:
    enabled: true
    agents: [fake]
    worktree:
      enabled: true
      root: .deliberate/worktrees
      cleanup: true

  review:
    enabled: false
    agents: []

limits:
  budget:
    max_total_tokens: 500000
    max_cost_usd: 10.0

# To use real agents:
# 1. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables
# 2. Or authenticate with LLM CLI tools (claude, gemini, etc.)
# 3. Run 'deliberate init --force' to regenerate config
"""


def configure_mcp_servers_interactive(
    agents: list[DetectedAgent],
) -> dict[str, dict[str, list[str]]]:
    """Interactively configure MCP servers for each agent and phase.

    Args:
        agents: List of detected agents with MCP servers

    Returns:
        Dict of {agent_name: {phase: [server_names]}}
    """
    from rich.console import Console
    from rich.prompt import Confirm, Prompt
    from rich.table import Table

    console = Console()
    config: dict[str, dict[str, list[str]]] = {}
    phases = ["planning", "execution", "review"]

    for agent in agents:
        if not agent.mcp_servers:
            continue

        console.print(f"\n[bold cyan]Configure MCP servers for {agent.name}[/bold cyan]")
        console.print(f"Found {len(agent.mcp_servers)} MCP server(s):\n")

        # Show available servers
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="dim")
        table.add_column("Source", style="dim")

        for server in agent.mcp_servers:
            cmd = server.command if isinstance(server.command, str) else " ".join(server.command)
            table.add_row(server.name, cmd[:50], server.source)

        console.print(table)
        console.print()

        if not Confirm.ask(f"Configure MCP servers for {agent.name}?", default=True):
            continue

        agent_config: dict[str, list[str]] = {phase: [] for phase in phases}

        for phase in phases:
            console.print(f"\n[bold]Phase: {phase}[/bold]")

            if not Confirm.ask(f"  Enable MCP servers for {phase}?", default=True):
                continue

            # Let user select servers for this phase
            available = [s.name for s in agent.mcp_servers]
            console.print(f"  Available servers: {', '.join(available)}")

            # Ask which servers to enable
            selected_input = Prompt.ask(
                "  Enter server names (comma-separated) or 'all' or 'none'",
                default="all",
            )

            if selected_input.lower() == "none":
                selected_servers = []
            elif selected_input.lower() == "all":
                selected_servers = available
            else:
                selected_servers = [s.strip() for s in selected_input.split(",")]
                # Validate
                invalid = [s for s in selected_servers if s not in available]
                if invalid:
                    console.print(f"  [yellow]Warning: Unknown servers: {', '.join(invalid)}[/yellow]")
                    selected_servers = [s for s in selected_servers if s in available]

            agent_config[phase] = selected_servers

        config[agent.name] = agent_config

    return config
