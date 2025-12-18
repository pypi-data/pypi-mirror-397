def normalize_channel_names(raw_names):
    """
    Normalize EEG channel names with safe, non-destructive rules.

    Rules applied:
    - strip whitespace
    - remove trailing dots
    - uppercase
    - preserve order and count

    Parameters
    ----------
    raw_names : list[str]

    Returns
    -------
    clean_names : list[str]
    """
    clean_names = []

    for name in raw_names:
        if not isinstance(name, str):
            clean_names.append(name)
            continue

        cleaned = name.strip()
        cleaned = cleaned.rstrip(".")
        cleaned = cleaned.upper()

        clean_names.append(cleaned)

    return clean_names