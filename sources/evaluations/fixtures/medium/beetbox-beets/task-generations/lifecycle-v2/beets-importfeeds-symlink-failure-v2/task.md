# Keep importing when a feed link cannot be created

An import stops with an error when the plugin that maintains a directory of links to imported music cannot create one of them. Link creation can fail for filesystem reasons that say nothing about the import itself, and the failure should be surfaced as a warning for that entry while the import proceeds.

Completion condition: a link that cannot be created produces a warning and the import continues.

Derived by reversing the production half of upstream `65a01c2c2a`; the covering upstream tests are test/plugins/test_importfeeds.py.
