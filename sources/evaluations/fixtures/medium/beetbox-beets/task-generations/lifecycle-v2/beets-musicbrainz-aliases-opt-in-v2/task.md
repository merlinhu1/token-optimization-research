# Make artist aliases-as-credits opt-in

Artist credits from MusicBrainz are always replaced by artist aliases. This changes tags for everyone whether they asked for it or not, and it should instead be a plugin setting that defaults to off, consulted where the credits are parsed.

Completion condition: alias substitution happens only when the corresponding plugin setting is enabled, and defaults to off.

Derived by reversing the production half of upstream `785f8b7a5c`; the covering upstream tests are test/plugins/test_musicbrainz.py.
