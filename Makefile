PYTHON ?= python3
SHELL := /bin/bash

.PHONY: check validate test runbook truthmark

# The full AGENTS.md required-checks gate. CI runs this target so the checklist
# has one executable definition instead of a prose copy that can drift.
#
# The final step enforces "a green run is invalid if it deleted a required test
# or left new evidence untracked" by comparing the tree before and after the
# checks, so it holds on a clean CI checkout and on a dirty local tree alike.
check:
	@before="$$(git status --porcelain)"; \
	status=0; \
	$(MAKE) --no-print-directory runbook validate truthmark || status=$$?; \
	git diff --check || status=$$?; \
	after="$$(git status --porcelain)"; \
	if [ "$$before" != "$$after" ]; then \
	  printf 'required checks changed the working tree.\nbefore:\n%s\nafter:\n%s\n' "$$before" "$$after"; \
	  status=1; \
	fi; \
	exit $$status

test:
	$(PYTHON) -m unittest -v \
	  scripts.test_workflow_evaluation_contract \
	  scripts.test_claude_code_usage_contract

validate: test
	$(PYTHON) scripts/validate_repository.py

runbook:
	$(PYTHON) scripts/update_workflow_runbook.py --check

truthmark:
	truthmark check --json
	truthmark index --json
