# Restore the replace command's subcommand invocation

The `replace` command fails as soon as it is invoked. Beets subcommands are called with the library, the parsed command-line options, and the remaining positional arguments, and this command's handler no longer accepts what the command framework passes it, so the call raises before any replacement work begins.

Completion condition: invoking the replace command runs its normal argument handling instead of failing at the call boundary.

Derived by reversing the production half of upstream `d06774b14d`; the covering upstream tests are test/plugins/test_replace.py.
