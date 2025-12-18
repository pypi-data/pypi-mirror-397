"""
MCP Integration Module

Provides utilities for integrating HCT signals with MCP clients/servers.
"""

from typing import Any, Optional

from ..schema import HCTSignal, SignalType
from ..schema import Performance as Performance


class MCPSignalExtension:
    """
    Helper for embedding HCT signals in MCP messages.

    Example:
        ext = MCPSignalExtension()

        # Add HCT signal to existing MCP params
        mcp_params = {"id": "task-123", "message": {...}}
        mcp_params = ext.embed_signal(mcp_params, signal)

        # Extract HCT signal from MCP response
        signal = ext.extract_signal(mcp_response)
    """

    EXTENSION_KEY = "hct_signal"

    def embed_signal(
        self, mcp_params: dict[str, Any], signal: HCTSignal
    ) -> dict[str, Any]:
        """
        Embed an HCT signal into MCP message params.

        Args:
            mcp_params: Existing MCP params dict
            signal: HCT signal to embed

        Returns:
            Updated params with hct_signal extension
        """
        result = dict(mcp_params)
        result[self.EXTENSION_KEY] = signal.model_dump(mode="json")
        return result

    def extract_signal(self, mcp_message: dict[str, Any]) -> Optional[HCTSignal]:
        """
        Extract HCT signal from MCP message.

        Args:
            mcp_message: MCP message dict (params or response)

        Returns:
            HCTSignal if present, None otherwise
        """
        sig_data = mcp_message.get(self.EXTENSION_KEY)
        if sig_data is None:
            return None
        return HCTSignal.from_mcp({self.EXTENSION_KEY: sig_data})

    def has_signal(self, mcp_message: dict[str, Any]) -> bool:
        """Check if MCP message contains HCT signal."""
        return self.EXTENSION_KEY in mcp_message

    def get_signal_type(self, mcp_message: dict[str, Any]) -> Optional[SignalType]:
        """Get signal type from MCP message without full parsing."""
        sig_data = mcp_message.get(self.EXTENSION_KEY)
        if sig_data is None:
            return None
        try:
            return SignalType(sig_data["type"])
        except (KeyError, ValueError):
            return None


def create_mcp_task_send(
    task_id: str, content: str, signal: HCTSignal, role: str = "user"
) -> dict[str, Any]:
    """
    Create a complete MCP tasks/send message with HCT signal.

    Example:
        msg = create_mcp_task_send(
            "task-123",
            "Analyze Q4 revenue",
            cue("orchestrator", ["analyst"], urgency=8)
        )
    """
    return {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "id": task_id,
            "message": {"role": role, "content": content},
            "hct_signal": signal.model_dump(mode="json"),
        },
    }


def create_mcp_task_subscribe(
    task_id: str, content: str, signal: HCTSignal, role: str = "user"
) -> dict[str, Any]:
    """
    Create an MCP tasks/sendSubscribe message with HCT signal.
    Used for FERMATA and VAMP signals that need response streaming.
    """
    return {
        "jsonrpc": "2.0",
        "method": "tasks/sendSubscribe",
        "params": {
            "id": task_id,
            "message": {"role": role, "content": content},
            "hct_signal": signal.model_dump(mode="json"),
        },
    }
