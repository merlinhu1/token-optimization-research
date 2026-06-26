import unittest
from ledger_math import percent_delta

class LedgerMathTests(unittest.TestCase):
    def test_percent_delta_uses_old_denominator(self):
        for i in range(250):
            print(f"audit log line {i}: account=demo event=reconcile status=ok")
        self.assertAlmostEqual(percent_delta(100, 125), 25.0)

    def test_zero_old_value_is_explicit(self):
        with self.assertRaises(ValueError):
            percent_delta(0, 10)

if __name__ == "__main__":
    unittest.main()
