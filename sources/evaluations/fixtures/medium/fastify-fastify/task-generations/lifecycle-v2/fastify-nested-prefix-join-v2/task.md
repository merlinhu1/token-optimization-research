# Join nested route prefixes without a doubled or missing separator

Registering a plugin under a nested prefix can produce a malformed route path. When the enclosing prefix already ends with a separator and the plugin's own prefix does not begin with one, a separator is added anyway and the joined path contains two. The existing handling of the opposite case must keep working.

Completion condition: nested prefixes join with exactly one separator in every combination of leading and trailing separators.

Derived by reversing the production half of upstream `2f597a9297`; the covering upstream tests are test/route-prefix.test.js.
