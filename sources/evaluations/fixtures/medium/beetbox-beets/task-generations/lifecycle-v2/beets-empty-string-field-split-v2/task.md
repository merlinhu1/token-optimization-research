# Do not split an empty single-value field into a list

Reading a single-value field that is empty and deriving its list counterpart searches the empty text for a separator, finds none, and takes a fallback path intended for text that simply has no separator in it. An empty value has nothing to split and should be left alone rather than routed through the splitting logic at all.

Completion condition: an empty single-value field yields no list entries instead of being split.

Derived by reversing the production half of upstream `7b59604c54`; the covering upstream tests are test/autotag/test_hooks.py.
