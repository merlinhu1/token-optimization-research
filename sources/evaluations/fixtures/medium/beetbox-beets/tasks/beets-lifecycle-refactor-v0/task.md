# Beets lifecycle task: lazy model storage refactor

## Classification

Behavior-preserving refactor.

## Authentic source

Derived from upstream Beets commit `8146d535af`, "Refactor lazy model value storage." The seed reverses only the production change in `beets/dbcore/db.py`; acceptance is behavior- and contract-based, never source-identity-based.

## Contract

Replace the bespoke lazy-conversion mapping with a `collections.UserDict`-backed implementation while preserving lazy SQL conversion, mutation, deletion, iteration, copying, missing-key, and model-loading behavior. Keep this as a structural refactor: no user-visible command or database behavior may change.
