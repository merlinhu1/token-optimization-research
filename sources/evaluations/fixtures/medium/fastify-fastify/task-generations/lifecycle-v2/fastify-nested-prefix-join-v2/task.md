# Join a nested route prefix with exactly one separator

Registering a plugin under a nested prefix produces a route path containing two consecutive separators whenever the enclosing prefix already ends with one and the plugin's own prefix does not begin with one. The opposite arrangement, where the plugin's prefix supplies the separator, is already handled and must keep working.

Completion condition: a nested prefix joins to its enclosing prefix with exactly one separator, whichever side supplies it.

Derived by reversing the production half of upstream `2f597a9297`; the covering upstream tests are test/route-prefix.test.js.
