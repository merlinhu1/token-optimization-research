# Reject a malformed relative date instead of crashing

A date query written with a stray pipe, as a user might type expecting it to mean 'or', crashes with an uncaught lookup error rather than the documented parse error. The pattern that recognises a relative date encloses its sign and its unit in character classes that also list a pipe, so the pipe is accepted as a valid unit and then fails when that unit is looked up.

Completion condition: a date query containing a stray pipe raises the documented parse error instead of an uncaught lookup failure.

Derived by reversing the production half of upstream `4a1e9164a1`; the covering upstream tests are test/dbcore/test_datequery.py.
