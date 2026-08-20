# Keep a short subcommand and its description on one line

In the listing of available subcommands, a name short enough to fit the column reserved for names is followed by a line break, so its description begins on the following line and the reserved column is left empty beside it. A name too long for that column is handled by a separate branch that is correct and must stay that way.

Completion condition: a subcommand whose name fits the reserved column is followed by its description on the same line.

Derived by reversing the production half of upstream `9e3f22b8be`; the covering upstream tests are test/ui/test_ui.py.
