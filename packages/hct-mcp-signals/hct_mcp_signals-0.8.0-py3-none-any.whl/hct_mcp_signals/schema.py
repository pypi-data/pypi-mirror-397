"""
HCT-MCP Signal Schema Definitions

Pydantic models for HCT coordination signals.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    """HCT coordination signal types."""

    CUE = "cue"  # Trigger agent activation
    FERMATA = "fermata"  # Hold for approval
    ATTACCA = "attacca"  # Immediate transition
    VAMP = "vamp"  # Repeat until condition
    CAESURA = "caesura"  # Full stop
    TACET = "tacet"  # Agent inactive
    DOWNBEAT = "downbeat"  # Global sync point


class Tempo(str, Enum):
    """Musical tempo indications for urgency mapping."""

    LARGO = "largo"  # Very slow (~1 min response OK)
    ANDANTE = "andante"  # Walking pace (~30s response)
    MODERATO = "moderato"  # Moderate (~15s response)
    ALLEGRO = "allegro"  # Fast (~5s response)
    PRESTO = "presto"  # Very fast (~1s response)


class HoldType(str, Enum):
    """Types of holds for FERMATA signals."""

    HUMAN = "human"  # Requires human approval
    GOVERNANCE = "governance"  # Requires governance check
    RESOURCE = "resource"  # Waiting for resource
    QUALITY = "quality"  # Quality threshold not met


class Performance(BaseModel):
    """Performance parameters (Layer 3 in HCT)."""

    urgency: int = Field(default=5, ge=1, le=10, description="1-10 urgency scale")
    tempo: Tempo = Field(default=Tempo.MODERATO, description="Expected response timing")
    timeout_ms: Optional[int] = Field(
        default=None, description="Timeout in milliseconds"
    )

    model_config = {"use_enum_values": True}


class Conditions(BaseModel):
    """Conditions for conditional signals (FERMATA, VAMP)."""

    hold_type: Optional[HoldType] = Field(default=None, description="Type of hold")
    repeat_until: Optional[str] = Field(default=None, description="Condition for VAMP")
    quality_threshold: Optional[float] = Field(
        default=None, ge=0, le=1, description="Quality score threshold"
    )

    model_config = {"use_enum_values": True}


class HCTSignal(BaseModel):
    """
    Complete HCT Signal for MCP extension.

    Example:
        signal = HCTSignal(
            type=SignalType.CUE,
            source="orchestrator",
            targets=["analyst"],
            payload={"task": "Analyze Q4"},
            performance=Performance(urgency=8, tempo=Tempo.ALLEGRO)
        )
        mcp_message = signal.to_mcp()
    """

    type: SignalType = Field(..., description="Signal type")
    source: str = Field(..., description="Source agent ID")
    targets: list[str] = Field(default_factory=list, description="Target agent IDs")
    payload: dict[str, Any] = Field(default_factory=dict, description="Signal payload")
    performance: Performance = Field(
        default_factory=Performance, description="Performance params"
    )
    conditions: Optional[Conditions] = Field(
        default=None, description="Conditional params"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Signal timestamp"
    )

    model_config = {"use_enum_values": True}

    def to_mcp(self) -> dict[str, Any]:
        """Convert to MCP-compatible JSON structure."""
        return {
            "hct_signal": {
                "type": self.type,
                "source": self.source,
                "targets": self.targets,
                "payload": self.payload,
                "performance": (
                    self.performance.model_dump() if self.performance else None
                ),
                "conditions": self.conditions.model_dump() if self.conditions else None,
                "timestamp": self.timestamp.isoformat(),
            }
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_mcp(), indent=2)

    @classmethod
    def from_mcp(cls, mcp_data: dict[str, Any]) -> "HCTSignal":
        """Parse from MCP message with hct_signal extension."""
        sig = mcp_data.get("hct_signal", mcp_data)
        return cls(
            type=SignalType(sig["type"]),
            source=sig["source"],
            targets=sig.get("targets", []),
            payload=sig.get("payload", {}),
            performance=(
                Performance(**sig["performance"])
                if sig.get("performance")
                else Performance()
            ),
            conditions=(
                Conditions(**sig["conditions"]) if sig.get("conditions") else None
            ),
        )
