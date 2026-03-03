# MCP Utilities

Tools for controlling an MCP23017 GPIO expander.

## mcp.py

Interactive command shell for toggling A0–A7 pins:

```bash
python mcp.py --address 0x20
```

Commands inside the shell:

- `set A0 on` / `set A0 off`
- `toggle A3`
- `status`
- `exit`

## mcp_gui.py

Graphical interface for toggling both A and B pins:

```bash
python mcp_gui.py --address 0x20
```

Click the buttons to toggle pins or use "Show Status" to view all pin states.
