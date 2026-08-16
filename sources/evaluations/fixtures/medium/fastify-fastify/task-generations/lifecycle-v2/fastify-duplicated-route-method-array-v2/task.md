# Report duplicated routes registered with several methods

Registering a route for more than one method at once loses the dedicated duplicate-route error when one of those methods is already declared. The check that recognises a duplicate assumes a single method value, so a multi-method registration is not matched and the caller receives an error without the framework's own error code.

Completion condition: a duplicate is recognised when any of the registered methods collides, and the framework's duplicate-route error is raised.

Derived by reversing the production half of upstream `d9659819fb`; the covering upstream tests are test/throw.test.js.
