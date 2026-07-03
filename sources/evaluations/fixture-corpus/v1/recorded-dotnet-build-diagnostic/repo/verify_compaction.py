from pathlib import Path
text = Path("artifacts/compacted.txt").read_text()
required = [
    "DiscountCalculator.cs",
    "42,28",
    "CS1503",
    "string",
    "decimal",
    "Billing.csproj",
    "raw/dotnet-build.log",
]
missing = [item for item in required if item not in text]
assert not missing, f"missing .NET diagnostic facts: {missing}"
print("dotnet diagnostic compaction verifier passed")
