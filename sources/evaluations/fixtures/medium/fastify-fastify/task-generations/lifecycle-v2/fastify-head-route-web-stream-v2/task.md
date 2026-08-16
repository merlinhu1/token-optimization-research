# Handle web stream payloads on automatic HEAD routes

A handler that returns a web stream breaks the automatically generated HEAD route. Node streams are recognised and disposed of without sending a body, but a web stream is not, so it falls through to the branch that measures a buffer's length. A web stream should be cancelled, with any cancellation failure logged, and the response completed with no body.

Completion condition: a HEAD request against a handler returning a web stream completes with no body and the stream cancelled.

Derived by reversing the production half of upstream `dd02e428dd`; the covering upstream tests are test/route.6.test.js, test/route.7.test.js.
