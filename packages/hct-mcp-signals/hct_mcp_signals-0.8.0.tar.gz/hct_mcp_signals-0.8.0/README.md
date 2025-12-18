# HCT MCP Signals (Python)

Python implementation of the Harmonic Coordination Theory (HCT) Signals extension for the Model Context Protocol (MCP).

## Installation

```bash
pip install hct-mcp-signals
```

## Usage

```python
from hct_mcp_signals import cue, tacet

# Create a CUE signal
signal = cue("orchestrator", ["analyst", "verifier"]).build()

# Embed in MCP
params = {"id": "task-123", "data": "..."}
params = embed_signal(params, signal)
```

See the [main repository](https://github.com/stefanwiest/hct-mcp-signals) for full documentation.
