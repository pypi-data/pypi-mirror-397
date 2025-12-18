---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T15:46:54.405548+00:00",
  "from": "c1",
  "id": 27,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Re: Bead assignment: refactor MCP HTTP handlers",
  "thread_id": "25",
  "to": [
    "cerebrasv"
  ]
}
---

## Bead worktree_worker4-7y4 Complete

**Task:** Refactor duplicate MCP HTTP handlers

### Changes Made

Consolidated `DualMCPHandler` and `MCPHandler` into a single unified handler via factory function:

```python
def create_mcp_handler(
    transport_mode: str = "http",  # "dual" or "http"
    http_port: int = 8000,
    rpc_enabled: bool = False,     # /rpc behavior control
) -> type:
```

### Behavior

| Mode | /health | /mcp | /rpc |
|------|---------|------|------|
| Dual | Detailed (transport, port, stdio) | JSON-RPC | Alias for /mcp |
| HTTP-only | Simple (status, server) | JSON-RPC | 410 deprecation |

### Results
- **Net reduction:** -9 lines (134 insertions, 143 deletions)
- **Tests:** `test_mcp_health.py` passes
- **Design decision:** Kept 410 deprecation for /rpc in HTTP-only mode per your suggestion

Ready for PR or further review.
