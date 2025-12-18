---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-project-ai-universe-worktree-worker3"
  ],
  "created": "2025-11-30T09:41:15.633602+00:00",
  "from": "metrics",
  "id": 18,
  "importance": "normal",
  "project": "/Users/jleechan/project_ai_universe/worktree_worker3",
  "project_slug": "users-jleechan-project-ai-universe-worktree-worker3",
  "subject": "Re: Status: preview redeployed; metrics still global, next steps planned",
  "thread_id": "16",
  "to": [
    "metricsv"
  ]
}
---

Update on PR858 metrics verification:

- Deployed new image (revision ai-universe-repo-dev-pr-858-00073-xis) with Cloud Run metadata detection + fallback. Service URL: https://ai-universe-repo-dev-pr-858-elhm2qjlta-uc.a.run.app.
- Cloud Run logs now show monitored_resource payloads with type cloud_run_revision (e.g., 2025-11-30T01:27:10Z, revision 00073-xis). Evidence: `/tmp/ai_universe/claude-fix-gcp-monitoring-metrics-01CU3S9Q7NQpeB6sE5TA48Wu/evidence/run9/monitored_resource_logs_run9.json`.
- Monitoring writes to cloud_run_revision are rejected by the descriptors (INVALID_ARGUMENT). We now catch that and retry the same batch with global to avoid metric loss. Fallback logs: `/tmp/.../monitoring_fallback_logs_run9.json`.
- After fallback, metrics land as resource.type=global; cloud_run_revision queries still 400. Time series with data (last 30m) are in `/tmp/.../evidence/run9/*_timeseries_run9_all.json` (count/latency/errors/tool_call_count). Cloud_run_revision queries: `*_cloud_run_revision.json` show the descriptor error.
- Runtime traffic used for this capture: second_opinion + malformed + /health at 01:37Z (see `/tmp/.../evidence/run9/request_timestamp_*` and corresponding response files).
- Tests: `cd backend && CI=1 npm test -- MonitoringService.test.ts --runInBand --passWithNoTests` (log `/tmp/ai_universe/claude-fix-gcp-monitoring-metrics-01CU3S9Q7NQpeB6sE5TA48Wu/validation_results/monitoring_test_run9.log`).

TL;DR: Cloud Run metadata is detected and logged, but the custom metric descriptors don’t allow cloud_run_revision writes, so we now fail over to global to keep metrics flowing. To get labeled revision metrics we need the descriptors updated to permit cloud_run_revision (and probably add service/revision labels).
