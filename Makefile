.PHONY: validate test

test:
	python3 -m unittest -v scripts.test_workflow_evaluation_contract

validate: test
	python3 scripts/validate_repository.py
