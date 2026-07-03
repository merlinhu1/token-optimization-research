def percent_delta(old, new):
    """Return percentage change from old to new."""
    if old == 0:
        raise ValueError("old value must be non-zero")
    return ((new - old) / new) * 100
