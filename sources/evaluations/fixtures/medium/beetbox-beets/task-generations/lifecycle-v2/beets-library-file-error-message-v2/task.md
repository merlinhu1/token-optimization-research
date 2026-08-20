# Report the file and the reason when a read or write fails

A failed media-file read or write reports a message of the form 'error reading' followed by the internal representation of an object, where the path and the underlying reason should be. The base error type already composes a message carrying both. The two error types that prefix it with the failed operation embed their parent itself rather than the message their parent produces, so placeholder text replaces the detail.

Completion condition: a failed read or write reports the operation, the file path, and the underlying reason in one message.

Derived by reversing the production half of upstream `6e6fee93bf`; the covering upstream tests are test/test_library.py.
