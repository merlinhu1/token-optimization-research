# Report the error raised inside a lazily computed attribute

When the body of a lazily computed attribute raises a missing-attribute error, the lookup machinery reads that as the attribute itself being absent and falls back to ordinary key lookup, so the reported failure names the outer attribute and the line that actually failed is lost. It has to surface as a failure the fallback does not intercept, still pointing at the original line, and reported once rather than as a chained pair of tracebacks.

Completion condition: an error raised inside a lazily computed attribute is reported once, against the line that raised it, instead of being masked by the attribute fallback.

Derived by reversing the production half of upstream `8a1f9d916a`; the covering upstream tests are test/autotag/test_hooks.py.
