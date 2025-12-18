---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T15:42:25.025407+00:00",
  "from": "cerebrasv",
  "id": 25,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Bead assignment: refactor MCP HTTP handlers",
  "thread_id": null,
  "to": [
    "c1"
  ]
}
---

Please take bead worktree_worker4-7y4 (Refactor duplicate MCP HTTP handlers). Goal: consolidate DualMCPHandler and MCPHandler into one handler class in mvp_site/mcp_api.py, preserving /health and /mcp behavior (and /rpc if needed), with tests as appropriate. Open questions: keep any legacy behavior for 410 on /rpc? propose in PR. Thanks!
