"""
HCT-MCP Signals: Coordination Signals Extension for MCP

Adds urgency, timing, and approval semantics to Model Context Protocol.
"""

from .factory import attacca, caesura, cue, downbeat, fermata, tacet, vamp
from .json_schema import (
    HCT_SIGNAL_EXTENSION_SCHEMA,
    export_json_schema,
    get_json_schema,
    get_json_schema_string,
)
from .mcp import (
    MCPSignalExtension,
    create_mcp_task_send,
    create_mcp_task_subscribe,
)
from .schema import (
    Conditions,
    HCTSignal,
    HoldType,
    Performance,
    SignalType,
    Tempo,
)

__version__ = "0.8.0"

__all__ = [
    "HCT_SIGNAL_EXTENSION_SCHEMA",
    "Conditions",
    "HCTSignal",
    "HoldType",
    # MCP Integration
    "MCPSignalExtension",
    "Performance",
    # Schema
    "SignalType",
    "Tempo",
    "attacca",
    "caesura",
    "create_mcp_task_send",
    "create_mcp_task_subscribe",
    # Factory
    "cue",
    "downbeat",
    "export_json_schema",
    "fermata",
    # JSON Schema
    "get_json_schema",
    "get_json_schema_string",
    "tacet",
    "vamp",
]
