# Keep a short subcommand's description on its own line

In the command listing, a subcommand whose name is short enough to share a line with its description is instead followed by a line break, so the description is pushed onto the next line and the column alignment the listing pays for is wasted. The separate handling of names too long to share a line must keep working.

Completion condition: a subcommand short enough to share its line is followed by its description on that line instead of a break.

Derived by reversing the production half of upstream `9e3f22b8be`; the covering upstream tests are test/ui/test_ui.py.
