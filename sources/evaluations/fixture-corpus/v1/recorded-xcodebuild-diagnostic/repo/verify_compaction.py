from pathlib import Path
text = Path("artifacts/compacted.txt").read_text()
required = ["TokenDemo", "CheckoutViewModel.swift", "87:21", "String", "URL", "raw/xcodebuild.log"]
missing = [item for item in required if item not in text]
assert not missing, f"missing diagnostic facts: {missing}"
print("xcodebuild compaction verifier passed")
