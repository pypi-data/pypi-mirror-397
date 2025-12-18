"""
JSON Schema Export

Generates JSON Schema for HCT signal validation in non-Python environments.
"""

import json
from pathlib import Path
from typing import Any

from .schema import HCTSignal


def get_json_schema() -> dict[str, Any]:
    """
    Get JSON Schema for HCT Signal extension.

    Returns:
        JSON Schema dict compatible with JSON Schema Draft 2020-12
    """
    return HCTSignal.model_json_schema()


def get_json_schema_string(indent: int = 2) -> str:
    """Get JSON Schema as formatted string."""
    return json.dumps(get_json_schema(), indent=indent)


def export_json_schema(path: str) -> None:
    """Export JSON Schema to file."""
    Path(path).write_text(get_json_schema_string())


# Pre-generated schema for the hct_signal extension field
HCT_SIGNAL_EXTENSION_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "HCT-MCP Signal Extension",
    "description": "HCT coordination signals for MCP messages",
    "type": "object",
    "properties": {"hct_signal": {"$ref": "#/$defs/HCTSignal"}},
    "$defs": {
        "HCTSignal": {
            "type": "object",
            "required": ["type", "source"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": [
                        "cue",
                        "fermata",
                        "attacca",
                        "vamp",
                        "caesura",
                        "tacet",
                        "downbeat",
                    ],
                },
                "source": {"type": "string"},
                "targets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                },
                "payload": {"type": "object", "default": {}},
                "performance": {"$ref": "#/$defs/Performance"},
                "conditions": {"$ref": "#/$defs/Conditions"},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        },
        "Performance": {
            "type": "object",
            "properties": {
                "urgency": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5,
                },
                "tempo": {
                    "type": "string",
                    "enum": ["largo", "andante", "moderato", "allegro", "presto"],
                    "default": "moderato",
                },
                "timeout_ms": {"type": "integer", "minimum": 0},
            },
        },
        "Conditions": {
            "type": "object",
            "properties": {
                "hold_type": {
                    "type": "string",
                    "enum": ["human", "governance", "resource", "quality"],
                },
                "repeat_until": {"type": "string"},
                "quality_threshold": {"type": "number", "minimum": 0, "maximum": 1},
            },
        },
    },
}
