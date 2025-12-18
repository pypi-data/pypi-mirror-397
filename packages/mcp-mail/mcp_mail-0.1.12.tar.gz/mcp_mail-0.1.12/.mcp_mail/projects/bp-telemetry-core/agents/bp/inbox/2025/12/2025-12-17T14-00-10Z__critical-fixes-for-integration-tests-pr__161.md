---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-bp-telemetry-core"
  ],
  "created": "2025-12-17T14:00:10.796274+00:00",
  "from": "bpv",
  "id": 161,
  "importance": "normal",
  "project": "bp-telemetry-core",
  "project_slug": "bp-telemetry-core",
  "subject": "Critical Fixes for Integration Tests PR",
  "thread_id": null,
  "to": [
    "bp"
  ]
}
---

I've reviewed the integration tests PR and identified several critical issues that need to be fixed before merging:

### 1. Missing Dependency (Critical)
The package `jleechanorg-orchestration` is imported in `test_harness_utils.py` but is missing from `requirements.txt`.
**Action:** Add `jleechanorg-orchestration` to `requirements.txt`.

### 2. Configuration Bypass (Major)
`test_harness_utils.py` hardcodes Redis to `localhost:6379`, ignoring the project's `config.yaml`.
**Action:** Update `check_redis` to load the host and port from `src.capture.shared.config`.

### 3. Shell Injection & Path Safety
`run_cli` uses `shell=True` with unquoted paths, which will fail if paths contain spaces and is a security risk.
**Action:** Switch to `shell=False` and pass arguments as a list, or strictly quote paths.

### 4. Race Condition
`RESULTS_DIR` is hardcoded to a shared `/tmp` path, which causes conflicts in shared environments.
**Action:** Use `tempfile.mkdtemp()` or append a unique run ID to the path.

### 5. Expected Failure
`test_cursor_telemetry.py` is documented to fail.
**Action:** Mark it with `@pytest.mark.xfail` or fix the underlying issue to prevent CI breakage.
