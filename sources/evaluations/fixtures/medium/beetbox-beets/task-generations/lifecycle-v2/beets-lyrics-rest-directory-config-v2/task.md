# Honor the configured ReST output directory for lyrics

The directory that lyrics are written to as ReST files can only be given on the command line. Setting it in configuration has no effect, because the option's default does not consult the plugin's configuration. The setting is optional and absent by default, and an explicit command-line value must still win.

Completion condition: the ReST output directory can be set in configuration, with the command-line option overriding it.

Derived by reversing the production half of upstream `478ac8cb63`; the covering upstream tests are test/plugins/test_lyrics.py.
