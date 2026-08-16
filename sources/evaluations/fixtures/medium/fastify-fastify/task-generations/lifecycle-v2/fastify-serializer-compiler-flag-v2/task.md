# Detect a custom serializer compiler correctly

An instance configured with a custom serializer compiler is not recognised as having one, while an instance with only a custom validator compiler is sometimes treated as though it had both. The flag that records whether a custom serializer compiler was supplied is derived from the wrong member of the compiler factory.

Completion condition: each custom-compiler flag reflects the presence of its own factory function.

Derived by reversing the production half of upstream `d76dbcd58b`; the covering upstream tests are test/internals/schema-controller-perf.test.js.
