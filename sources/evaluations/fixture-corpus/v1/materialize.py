#!/usr/bin/env python3
from pathlib import Path
import shutil, sys

BASE = Path(__file__).resolve().parent
FILES = {'go-interface-cache-repair': {'cache/cache.go': 'package cache\n'
                                                 '\n'
                                                 'import "context"\n'
                                                 '\n'
                                                 'type Store interface {\n'
                                                 '    Put(ctx context.Context, key string, value []byte) error\n'
                                                 '    Get(ctx context.Context, key string) ([]byte, error)\n'
                                                 '}\n'
                                                 '\n'
                                                 'type MemoryStore struct {\n'
                                                 '    data map[string][]byte\n'
                                                 '}\n'
                                                 '\n'
                                                 'func NewMemoryStore() *MemoryStore {\n'
                                                 '    return &MemoryStore{data: map[string][]byte{}}\n'
                                                 '}\n'
                                                 '\n'
                                                 'func (m *MemoryStore) Put(key string, value []byte) error {\n'
                                                 '    m.data[key] = value\n'
                                                 '    return nil\n'
                                                 '}\n'
                                                 '\n'
                                                 'func (m *MemoryStore) Get(ctx context.Context, key string) ([]byte, '
                                                 'error) {\n'
                                                 '    return m.data[key], nil\n'
                                                 '}\n',
                               'cache/cache_test.go': 'package cache\n'
                                                      '\n'
                                                      'import (\n'
                                                      '    "context"\n'
                                                      '    "testing"\n'
                                                      ')\n'
                                                      '\n'
                                                      'func TestMemoryStoreImplementsStore(t *testing.T) {\n'
                                                      '    var store Store = NewMemoryStore()\n'
                                                      '    if err := store.Put(context.Background(), "alpha", '
                                                      '[]byte("one")); err != nil {\n'
                                                      '        t.Fatalf("put failed: %v", err)\n'
                                                      '    }\n'
                                                      '    got, err := store.Get(context.Background(), "alpha")\n'
                                                      '    if err != nil {\n'
                                                      '        t.Fatalf("get failed: %v", err)\n'
                                                      '    }\n'
                                                      '    if string(got) != "one" {\n'
                                                      '        t.Fatalf("got %q", string(got))\n'
                                                      '    }\n'
                                                      '}\n',
                               'go.mod': 'module example.com/cachebench\n\ngo 1.23\n'},
 'node-esm-import-repair': {'package.json': '{"type":"module","scripts":{"test":"node --test"}}\n',
                            'src/cart.js': "import { normalizeSKU } from './normalize.js';\n"
                                           '\n'
                                           'export function addLine(cart, sku, qty) {\n'
                                           '  const key = normalizeSKU(sku);\n'
                                           '  return { ...cart, [key]: (cart[key] ?? 0) + qty };\n'
                                           '}\n',
                            'src/normalize.js': 'export function normalizeSku(value) {\n'
                                                '  return value.trim().toUpperCase();\n'
                                                '}\n',
                            'test/cart.test.js': "import test from 'node:test';\n"
                                                 "import assert from 'node:assert/strict';\n"
                                                 "import { addLine } from '../src/cart.js';\n"
                                                 '\n'
                                                 "test('normalizes SKU when adding cart line', () => {\n"
                                                 "  assert.deepEqual(addLine({}, ' abc-123 ', 2), { 'ABC-123': 2 });\n"
                                                 '});\n'},
 'py-noisy-unit-failure': {'ledger_math.py': 'def percent_delta(old, new):\n'
                                             '    """Return percentage change from old to new."""\n'
                                             '    if old == 0:\n'
                                             '        raise ValueError("old value must be non-zero")\n'
                                             '    return ((new - old) / new) * 100\n',
                           'tests/test_ledger_math.py': 'import unittest\n'
                                                        'from ledger_math import percent_delta\n'
                                                        '\n'
                                                        'class LedgerMathTests(unittest.TestCase):\n'
                                                        '    def test_percent_delta_uses_old_denominator(self):\n'
                                                        '        for i in range(250):\n'
                                                        '            print(f"audit log line {i}: account=demo '
                                                        'event=reconcile status=ok")\n'
                                                        '        self.assertAlmostEqual(percent_delta(100, 125), '
                                                        '25.0)\n'
                                                        '\n'
                                                        '    def test_zero_old_value_is_explicit(self):\n'
                                                        '        with self.assertRaises(ValueError):\n'
                                                        '            percent_delta(0, 10)\n'
                                                        '\n'
                                                        'if __name__ == "__main__":\n'
                                                        '    unittest.main()\n'},
 'recorded-dotnet-build-diagnostic': {'artifacts/.gitkeep': '',
                                      'raw/dotnet-build.log': 'MSBuild version 17.8.3+195e7f5a3 for .NET\n'
                                                              '  Determining projects to restore...\n'
                                                              '  All projects are up-to-date for restore.\n'
                                                              '/agent/workspace/src/Billing/DiscountCalculator.cs(42,28): '
                                                              "error CS1503: Argument 1: cannot convert from 'string' "
                                                              "to 'decimal' "
                                                              '[/agent/workspace/src/Billing/Billing.csproj]\n'
                                                              '/agent/workspace/src/Billing/InvoiceService.cs(88,17): '
                                                              'warning CS8602: Dereference of a possibly null '
                                                              'reference. '
                                                              '[/agent/workspace/src/Billing/Billing.csproj]\n'
                                                              '\n'
                                                              'Build FAILED.\n'
                                                              '\n'
                                                              '/agent/workspace/src/Billing/InvoiceService.cs(88,17): '
                                                              'warning CS8602: Dereference of a possibly null '
                                                              'reference. '
                                                              '[/agent/workspace/src/Billing/Billing.csproj]\n'
                                                              '/agent/workspace/src/Billing/DiscountCalculator.cs(42,28): '
                                                              "error CS1503: Argument 1: cannot convert from 'string' "
                                                              "to 'decimal' "
                                                              '[/agent/workspace/src/Billing/Billing.csproj]\n'
                                                              '    1 Warning(s)\n'
                                                              '    1 Error(s)\n',
                                      'verify_compaction.py': 'from pathlib import Path\n'
                                                              'text = Path("artifacts/compacted.txt").read_text()\n'
                                                              'required = [\n'
                                                              '    "DiscountCalculator.cs",\n'
                                                              '    "42,28",\n'
                                                              '    "CS1503",\n'
                                                              '    "string",\n'
                                                              '    "decimal",\n'
                                                              '    "Billing.csproj",\n'
                                                              '    "raw/dotnet-build.log",\n'
                                                              ']\n'
                                                              'missing = [item for item in required if item not in '
                                                              'text]\n'
                                                              'assert not missing, f"missing .NET diagnostic facts: '
                                                              '{missing}"\n'
                                                              'print("dotnet diagnostic compaction verifier '
                                                              'passed")\n'},
 'recorded-xcodebuild-diagnostic': {'artifacts/.gitkeep': '',
                                    'raw/xcodebuild.log': 'Command line invocation:\n'
                                                          '    '
                                                          '/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild '
                                                          '-scheme TokenDemo -destination platform=iOS '
                                                          'Simulator,name=iPhone 15 test\n'
                                                          '\n'
                                                          'Build target TokenDemo of project TokenDemo with '
                                                          'configuration Debug\n'
                                                          'SwiftCompile normal arm64 '
                                                          '/Users/research/TokenDemo/Sources/CheckoutViewModel.swift\n'
                                                          '/Users/research/TokenDemo/Sources/CheckoutViewModel.swift:87:21: '
                                                          "error: cannot convert value of type 'String' to expected "
                                                          "argument type 'URL'\n"
                                                          '        openReceipt(receiptPath)\n'
                                                          '                    ^~~~~~~~~~~\n'
                                                          'Testing failed:\n'
                                                          "    cannot convert value of type 'String' to expected "
                                                          "argument type 'URL'\n"
                                                          '** TEST FAILED **\n',
                                    'verify_compaction.py': 'from pathlib import Path\n'
                                                            'text = Path("artifacts/compacted.txt").read_text()\n'
                                                            'required = ["TokenDemo", "CheckoutViewModel.swift", '
                                                            '"87:21", "String", "URL", "raw/xcodebuild.log"]\n'
                                                            'missing = [item for item in required if item not in '
                                                            'text]\n'
                                                            'assert not missing, f"missing diagnostic facts: '
                                                            '{missing}"\n'
                                                            'print("xcodebuild compaction verifier passed")\n'}}


def reset(fid):
    if fid not in FILES:
        raise SystemExit(f"unknown fixture {fid}")
    repo = BASE / fid / "repo"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    for rel, content in FILES[fid].items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    ids = sorted(FILES) if len(sys.argv) == 1 or sys.argv[1] == "all" else sys.argv[1:]
    for fid in ids:
        reset(fid)
        print(f"materialized {fid}")
