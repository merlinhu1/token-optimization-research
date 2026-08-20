# Surface the real failure inside a cached attribute

When the body of a lazily computed attribute raises a missing-attribute error, the attribute machinery treats it as the attribute itself being absent and falls back, so the reported failure names the outer attribute and hides where the error really came from. The failure should be re-raised as a different error class that stops the fallback, must still point at the line that actually failed, and must not print a second chained traceback for the same event.

Completion condition: a missing-attribute failure inside a lazily computed attribute is reported against the line that raised it, without a chained duplicate traceback.

Derived by reversing the production half of upstream `8a1f9d916a`; the covering upstream tests are test/autotag/test_hooks.py.
