#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
. .venv/bin/activate
PYTHONPATH=. python tests/runtests.py serializers.test_xml.XmlSerializerTestCase.test_control_char_failure_attribute syndication_tests.tests.SyndicationFeedTest.test_no_control_chars_in_attributes --verbosity 2
