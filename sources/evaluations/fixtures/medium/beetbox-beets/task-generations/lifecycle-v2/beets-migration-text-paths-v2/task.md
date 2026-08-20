# Complete the relative-path conversion on a hand-edited database

Converting a library to store paths relative to its root aborts when a stored path is text rather than bytes, which is what a user gets after editing the database directly with sqlite. The conversion assumes bytes. The same pass first collects the rows it intends to convert, and that collection includes rows holding no path at all, which cannot be converted and must be excluded before the conversion runs.

Completion condition: the relative-path conversion excludes rows with no stored path and succeeds on rows whose path was stored as text.

Derived by reversing the production half of upstream `2e3ca0a018`; the covering upstream tests are test/library/test_migrations.py.
