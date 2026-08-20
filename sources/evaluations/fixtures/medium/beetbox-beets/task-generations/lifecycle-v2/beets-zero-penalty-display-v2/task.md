# List only the penalties that actually applied

The summary of why a match was penalised lists every penalty the comparison can produce, including those that scored nothing. A penalty that contributed no distance is not a reason the match was downgraded and should not appear among the reasons shown.

Completion condition: the listed penalties include only those with a non-zero contribution.

Derived by reversing the production half of upstream `a734b9bce1`; the covering upstream tests are test/autotag/test_distance.py.
