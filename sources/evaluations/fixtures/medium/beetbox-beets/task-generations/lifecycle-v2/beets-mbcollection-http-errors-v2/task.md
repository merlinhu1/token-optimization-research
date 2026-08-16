# Handle MusicBrainz collection HTTP failures gracefully

Updating a MusicBrainz collection lets a failed HTTP request escape as an unhandled error, ending the command. A remote service that is unreachable or returns an error is an expected condition for this operation and should be reported through the plugin's logging rather than terminating the run.

Completion condition: an HTTP failure during a collection update is reported and handled instead of propagating.

Derived by reversing the production half of upstream `a0a88b5301`; the covering upstream tests are test/plugins/test_mbcollection.py.
