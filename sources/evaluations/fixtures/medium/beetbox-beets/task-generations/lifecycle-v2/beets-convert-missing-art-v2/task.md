# Skip album art that is recorded but absent

Converting an album whose stored art path points at a file that no longer exists aborts the conversion. A recorded art path is not a guarantee that the file is present -- the cover may live in the album root rather than a per-disc directory -- and a missing source should be reported and stepped over rather than ending the run.

Completion condition: conversion continues, logging the skipped art, when the recorded art file is not present.

Derived by reversing the production half of upstream `755ca6f139`; the covering upstream tests are test/plugins/test_convert.py.
