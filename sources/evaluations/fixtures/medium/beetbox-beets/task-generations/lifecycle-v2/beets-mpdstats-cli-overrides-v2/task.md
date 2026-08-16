# Restore mpdstats command-line connection overrides

The mpdstats command ignores the MPD host, port, and password given on the command line and always uses the configured values. Options supplied for a single invocation are expected to take precedence over configuration for that invocation only, and the decoding each option needs differs between them.

Completion condition: host, port, and password supplied on the command line override the configured values for that run.

Derived by reversing the production half of upstream `cf7c5e4eb2`; the covering upstream tests are test/plugins/test_mpdstats.py.
