from pathlib import Path
from eegcanon.io.registry import LOADER_REGISTRY


def load_file(path: str):
    """
    Load an EEG file using the registered loader based on file extension.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()

    if ext not in LOADER_REGISTRY:
        supported = ", ".join(LOADER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported file format '{ext}'. "
            f"Supported formats: {supported}"
        )

    loader = LOADER_REGISTRY[ext]
    return loader(path)