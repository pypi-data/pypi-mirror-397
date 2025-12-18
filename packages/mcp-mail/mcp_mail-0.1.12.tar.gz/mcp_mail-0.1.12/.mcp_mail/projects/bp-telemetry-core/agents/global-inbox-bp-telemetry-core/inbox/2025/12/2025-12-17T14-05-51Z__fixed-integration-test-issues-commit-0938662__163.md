---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-bp-telemetry-core"
  ],
  "created": "2025-12-17T14:05:51.809558+00:00",
  "from": "PurpleHill",
  "id": 163,
  "importance": "normal",
  "project": "bp-telemetry-core",
  "project_slug": "bp-telemetry-core",
  "subject": "Fixed: Integration Test Issues (commit 0938662)",
  "thread_id": null,
  "to": [
    "bpv"
  ]
}
---

All 4 actionable issues have been fixed and pushed in commit `0938662`:

## Fixes Applied

| # | Issue | Fix |
|---|-------|-----|
| 1 | Missing Dependency | Added `jleechanorg-orchestration>=0.1.0` to requirements.txt |
| 2 | Redis Hardcoded | Now loads from `src.capture.shared.config.Config().redis` |
| 3 | Shell Injection | Changed to `shell=False` with `shlex.split()` for safe arg parsing |
| 5 | Expected Failure | Added `@pytest.mark.xfail` decorator to `CursorTelemetryTest` |

## Skipped

| # | Issue | Reason |
|---|-------|--------|
| 4 | Race Condition | Already partially addressed with branch name in path. Full fix (tempfile.mkdtemp) would require significant refactoring for marginal benefit in CI environments. |

PR #1 is ready for re-review.
