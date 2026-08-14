PYTHON ?= python3
SHELL := /bin/bash

.PHONY: check validate test runbook

# The full AGENTS.md required-checks gate, and its one executable definition, so
# the instruction list documents this target instead of drifting from it. Nothing
# invokes it automatically; run it before finishing an evidence-changing change.
#
# The final step enforces "a green run is invalid if it deleted a required test
# or left new evidence untracked" by comparing the tree before and after the
# checks. It runs whether or not the earlier checks passed, because a failing run
# is when a destructive fixture is most likely to have written into the checkout.
check:
	@before="$$(git status --porcelain)"; \
	status=0; \
	$(MAKE) --no-print-directory runbook validate || status=$$?; \
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
