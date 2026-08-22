# Allow a run to override the keep-synced setting

The switch that skips items already holding synced lyrics can only be turned on from the command line. When the configuration enables it there is no way to turn it off for a single run, so a manual fetch cannot be forced to reprocess those items. Its help text also describes re-downloading rather than skipping, which is the opposite of what it does.

Completion condition: the keep-synced behaviour can be switched off for one run from the command line, and its help text describes what it does.

Derived by reversing the production half of upstream `d9a1bde1c9`; the covering upstream tests are test/plugins/test_lyrics.py.
