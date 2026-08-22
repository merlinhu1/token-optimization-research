# Continue a unique-name counter past nine

When a destination file already exists, a numeric suffix is appended and incremented until the name is free. Once the existing suffix reaches two or more digits the counter restarts near zero instead of continuing, because the pattern that reads the existing suffix captures only its final digit. Single-digit suffixes already behave correctly.

Completion condition: an existing numeric suffix of any length is read whole, so the next free name continues from it.

Derived by reversing the production half of upstream `a8439e2d07`; the covering upstream tests are test/test_util.py.
