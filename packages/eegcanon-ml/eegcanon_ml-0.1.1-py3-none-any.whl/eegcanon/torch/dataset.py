import torch
from torch.utils.data import Dataset
from pathlib import Path

from eegcanon.pipeline import load_eeg


class EEGDataset(Dataset):
    """
    PyTorch Dataset for EEG data using CanonicalEEG pipeline.
    """

    def __init__(
        self,
        data_dir: str,
        target_fs: float = 256.0,
        extensions=(".edf", ".csv"),
    ):
        self.data_dir = Path(data_dir)
        self.target_fs = target_fs
        self.extensions = extensions

        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        self.files = sorted(
            p for p in self.data_dir.iterdir()
            if p.suffix.lower() in self.extensions
        )

        if not self.files:
            raise ValueError("No EEG files found in directory")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        path = self.files[idx]

        eeg = load_eeg(
            path=str(path),
            target_fs=self.target_fs,
        )

        # Convert to torch tensor
        X = torch.tensor(eeg.data, dtype=torch.float32)

        return X, eeg