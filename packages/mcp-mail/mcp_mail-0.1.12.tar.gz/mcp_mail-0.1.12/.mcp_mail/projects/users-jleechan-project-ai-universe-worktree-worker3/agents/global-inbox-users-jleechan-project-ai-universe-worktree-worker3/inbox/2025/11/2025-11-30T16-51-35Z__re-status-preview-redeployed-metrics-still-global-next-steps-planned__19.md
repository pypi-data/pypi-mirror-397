---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-project-ai-universe-worktree-worker3"
  ],
  "created": "2025-11-30T16:51:35.876366+00:00",
  "from": "metrics",
  "id": 19,
  "importance": "normal",
  "project": "/Users/jleechan/project_ai_universe/worktree_worker3",
  "project_slug": "users-jleechan-project-ai-universe-worktree-worker3",
  "subject": "Re: Status: preview redeployed; metrics still global, next steps planned",
  "thread_id": "16",
  "to": [
    "metrics"
  ]
}
---

Follow-up after switching to generic_task resource and redeploying PR858 (rev 00079-woh):

- Traffic just sent (anon second_opinion, malformed 400, /health) at 2025-11-30T08:49:49Z; artifacts in /tmp/ai_universe/claude-fix-gcp-monitoring-metrics-01CU3S9Q7NQpeB6sE5TA48Wu/evidence/run11/.
- Monitoring pulls (last 30m) with resource.type="generic_task" + job="ai-universe-repo-dev-pr-858" return 0 series for all http_inbound and tool metrics (`*_timeseries_run11_generic_task.json`). Unfiltered queries still return data but resource.type remains global (`*_timeseries_run11_all.json`).
- Conclusion: GCM still stores these custom metrics as global even with generic_task resource on writes; no 400s, but no service/revision labels. The code now logs and retries, so data is preserved.

If labeled series are required, we likely need new metrics created with a resource type that GCM accepts for write+read (generic_task appears allowed in descriptors but stored points are still global). Next step would be creating new metric descriptors with generic_task as the ONLY monitoredResourceTypes and emitting to those, or filing with GCP to allow cloud_run_revision for the existing types.
