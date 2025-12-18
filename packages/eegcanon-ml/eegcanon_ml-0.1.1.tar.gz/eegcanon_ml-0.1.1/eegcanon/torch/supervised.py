import torch
import pandas as pd
from pathlib import Path
from torch.utils.data import Dataset

from eegcanon.pipeline import load_eeg


class EEGSupervisedDataset(Dataset):
    """
    Supervised EEG Dataset using CanonicalEEG.
    """

    def __init__(
        self,
        data_dir: str,
        labels_csv: str,
        target_fs: float = 256.0,
        window: float = 2.0,
        overlap: float = 0.5,
        feature_list=None,
        extensions=(".edf", ".csv"),
    ):
        self.data_dir = Path(data_dir)
        self.labels = pd.read_csv(labels_csv)
        self.target_fs = target_fs
        self.window = window
        self.overlap = overlap
        self.feature_list = feature_list
        self.extensions = extensions

        self.labels.set_index("file", inplace=True)

        self.files = sorted(
            p for p in self.data_dir.iterdir()
            if p.suffix.lower() in extensions and p.name in self.labels.index
        )

        if not self.files:
            raise ValueError("No labeled EEG files found")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        path = self.files[idx]

        eeg = load_eeg(
            path=str(path),
            target_fs=self.target_fs,
        )

        if self.feature_list:
            X = eeg.extract_features(
                feature_list=self.feature_list,
                window=self.window,
                overlap=self.overlap,
            )
            X = torch.tensor(X, dtype=torch.float32)
        else:
            epochs = eeg.to_epochs(
                window=self.window,
                overlap=self.overlap,
            )
            X = torch.tensor(epochs, dtype=torch.float32)

        y = self.labels.loc[path.name, "label"]
        y = torch.tensor(y)

        return X, y