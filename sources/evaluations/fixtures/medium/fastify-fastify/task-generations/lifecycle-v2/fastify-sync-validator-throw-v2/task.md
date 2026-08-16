# Convert a synchronously thrown validator error into an internal error

A custom validator that throws synchronously escapes the validation path uncaught, so the failure surfaces differently from the same fault in an asynchronous validator. A validator that throws is a server-side fault and must be reported as an internal error through the normal error path.

Completion condition: a synchronously thrown validator error is captured and reported as an internal server error.

Derived by reversing the production half of upstream `d338dca5ab`; the covering upstream tests are test/validation-error-handling.test.js.
