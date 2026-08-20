# Migrate stored paths that were saved as text

Converting a library to relative paths fails for users whose path values were set by hand through sqlite rather than written by the application, because those values come back as text where the migration expects bytes. The same scan also reads rows whose path is unset, which it cannot migrate and must not consider. Both the selection and the conversion need to account for this.

Completion condition: the relative-path migration skips rows with no stored path and converts text path values without failing.

Derived by reversing the production half of upstream `2e3ca0a018`; the covering upstream tests are test/library/test_migrations.py.
