# Dispatch each metadata plugin to its own concurrent call

Querying metadata sources concurrently returns the results of one source repeated instead of the results of each. The work submitted for every source closes over the loop variable rather than binding the source it was created for, so by the time the submitted work runs the variable holds whichever source was last in the sequence and every call targets that one.

Completion condition: each metadata source contributes its own results when sources are queried concurrently.

Derived by reversing the production half of upstream `ca36df2d00`; the covering upstream tests are test/test_metadata_plugins.py.
