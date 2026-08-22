# Extract a Spotify identifier from a native URI

Pasting a native Spotify URI of the form used by the desktop application, rather than a web link, yields no identifier at all. The pattern that recognises Spotify identifiers accepts a bare identifier and a web URL, but has no branch for the URI form, so extraction returns nothing. The two forms already recognised must keep working.

Completion condition: a native Spotify URI yields the same identifier as the equivalent web link.

Derived by reversing the production half of upstream `6a051f9699`; the covering upstream tests are test/util/test_id_extractors.py.
