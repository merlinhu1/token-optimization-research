# Make a membership query hashable when its pattern is a sequence

Hashing a query that tests membership in a collection raises an unhashable-type error whenever the collection is a list, which breaks any caller that puts such a query in a set or dictionary. The inherited hashing hashes the pattern directly, and a sequence pattern cannot be hashed as-is.

Completion condition: a membership query hashes successfully whether its pattern is a list or another sequence.

Derived by reversing the production half of upstream `eb7c832fc9`; the covering upstream tests are test/dbcore/test_query.py.
