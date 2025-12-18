"""Adapter modules for different LLM backends."""

from deliberate.adapters.base import AdapterResponse, ModelAdapter, ResourceInfo, ToolInfo
from deliberate.adapters.cli_adapter import CLIAdapter, MCPServerConfig
from deliberate.adapters.fake_adapter import FakeAdapter
from deliberate.adapters.mcp_adapter import MCPAdapter

__all__ = [
    "ModelAdapter",
    "AdapterResponse",
    "ToolInfo",
    "ResourceInfo",
    "CLIAdapter",
    "MCPServerConfig",
    "FakeAdapter",
    "MCPAdapter",
]
