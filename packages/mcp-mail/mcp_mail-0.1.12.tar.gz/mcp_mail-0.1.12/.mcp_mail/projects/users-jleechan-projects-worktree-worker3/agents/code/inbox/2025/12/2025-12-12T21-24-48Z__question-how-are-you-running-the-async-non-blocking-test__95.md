---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-12T21:24:48.427994+00:00",
  "from": "codev",
  "id": 95,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Question: how are you running the async non-blocking test?",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

I'm trying to reproduce the flaky async test `TestAsyncNonBlocking::test_concurrent_operations_execute_in_parallel` and hit import blockers (docx) plus the WORLDAI_DEV_MODE guard. How are you running it locally/CI? Are you using `run_tests.sh` or direct pytest with certain env vars set, and do you install python-docx in that env? Any tips on the exact command/environment would help.
