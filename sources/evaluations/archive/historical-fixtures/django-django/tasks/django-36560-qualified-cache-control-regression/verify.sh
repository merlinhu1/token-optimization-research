#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
. .venv/bin/activate
PYTHONPATH=. python tests/runtests.py cache.tests.CacheUtils.test_patch_cache_control_whitespace_around_equals cache.tests.CacheMiddlewareTest.test_qualified_cache_control_value_not_cached cache.tests.CacheMiddlewareTest.test_authorization_header_exception_qualified_public_directive middleware.tests.ConditionalGetMiddlewareTest.test_no_etag_no_store_qualified utils_tests.test_http.SplitDirectiveNamesTests.test_basic --verbosity 2
