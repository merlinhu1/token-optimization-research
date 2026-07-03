#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
. .venv/bin/activate
PYTHONPATH=. python tests/runtests.py admin_inlines.tests.TestInline.test_delete_protected_message_limits_number_of_objects_displayed admin_inlines.tests.TestInline.test_delete_protected_message_does_not_limit_small_amount_of_objects modeladmin.test_checks.DeleteConfirmationMaxObjectsCheckTests.test_inline_not_integer --verbosity 2
