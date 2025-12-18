"""
HCT Signal Factory Functions

Convenience functions for creating HCT signals.
"""

from typing import Any, Optional

from .schema import Conditions, HCTSignal, HoldType, Performance, SignalType, Tempo


def cue(
    source: str,
    targets: list[str],
    payload: Optional[dict[str, Any]] = None,
    urgency: int = 5,
    tempo: str = "moderato",
) -> HCTSignal:
    """Create a CUE signal to trigger agent activation."""
    return HCTSignal(
        type=SignalType.CUE,
        source=source,
        targets=targets,
        payload=payload or {},
        performance=Performance(urgency=urgency, tempo=Tempo(tempo)),
    )


def fermata(
    source: str, reason: str, hold_type: str = "human", timeout_ms: Optional[int] = None
) -> HCTSignal:
    """Create a FERMATA signal to hold for approval."""
    return HCTSignal(
        type=SignalType.FERMATA,
        source=source,
        targets=["governance"],
        payload={"reason": reason},
        performance=Performance(timeout_ms=timeout_ms),
        conditions=Conditions(hold_type=HoldType(hold_type)),
    )


def attacca(
    source: str, targets: list[str], payload: Optional[dict[str, Any]] = None
) -> HCTSignal:
    """Create an ATTACCA signal for immediate transition."""
    return HCTSignal(
        type=SignalType.ATTACCA,
        source=source,
        targets=targets,
        payload=payload or {},
        performance=Performance(urgency=10, tempo=Tempo.PRESTO),
    )


def vamp(
    source: str,
    repeat_until: str,
    quality_threshold: float = 0.9,
    timeout_ms: int = 60000,
) -> HCTSignal:
    """Create a VAMP signal to repeat until condition met."""
    return HCTSignal(
        type=SignalType.VAMP,
        source=source,
        targets=[source],  # Self-loop
        payload={},
        performance=Performance(timeout_ms=timeout_ms),
        conditions=Conditions(
            repeat_until=repeat_until, quality_threshold=quality_threshold
        ),
    )


def caesura(source: str, reason: str) -> HCTSignal:
    """Create a CAESURA signal for full stop."""
    return HCTSignal(
        type=SignalType.CAESURA,
        source=source,
        targets=["*"],  # Broadcast
        payload={"reason": reason},
        performance=Performance(urgency=10, tempo=Tempo.PRESTO),
    )


def tacet(source: str, duration_ms: Optional[int] = None) -> HCTSignal:
    """Create a TACET signal to mark agent as inactive."""
    return HCTSignal(
        type=SignalType.TACET,
        source=source,
        targets=[],
        payload={"duration_ms": duration_ms} if duration_ms else {},
    )


def downbeat(source: str, sync_point: str) -> HCTSignal:
    """Create a DOWNBEAT signal for global synchronization."""
    return HCTSignal(
        type=SignalType.DOWNBEAT,
        source=source,
        targets=["*"],  # Broadcast
        payload={"sync_point": sync_point},
    )
