# Derive each custom-compiler flag from its own factory function

An instance given a custom serializer compiler is not recorded as having one, and an instance given only a custom validator compiler is recorded as having both. The two flags that record which custom compilers were supplied are read from the same member of the compiler factory, so the serializer flag reports whether a validator was supplied.

Completion condition: the validator flag reflects a supplied validator compiler and the serializer flag reflects a supplied serializer compiler, independently.

Derived by reversing the production half of upstream `d76dbcd58b`; the covering upstream tests are test/internals/schema-controller-perf.test.js.
