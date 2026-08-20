# Restore the path and reason in file read and write errors

When reading or writing a media file fails, the reported error says only that a read or a write failed. The path that failed and the underlying reason are both lost, although the base error class already knows them and formats them into a message. The subclasses interpolate their parent into a string without asking it for that message, so what reaches the user is the placeholder text of an object rather than the detail the parent produced.

Completion condition: a failed read or write reports the file path and the underlying reason alongside the operation that failed.

Derived by reversing the production half of upstream `6e6fee93bf`; the covering upstream tests are test/test_library.py.
