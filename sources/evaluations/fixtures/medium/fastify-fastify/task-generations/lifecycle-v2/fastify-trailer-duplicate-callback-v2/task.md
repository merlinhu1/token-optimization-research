# Ignore duplicate trailer callback invocations

A trailer callback that is invoked more than once -- which happens when a handler mixes a callback with an async return -- is counted more than once, so the bookkeeping that tracks outstanding trailers is wrong and the response can be finalised at the wrong time. Only the first invocation of a given trailer callback should have any effect.

Completion condition: a trailer callback invoked repeatedly is honoured once and ignored thereafter.

Derived by reversing the production half of upstream `9026164f5a`; the covering upstream tests are test/reply-trailers.test.js.
