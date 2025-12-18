from eegcanon.io.load_edf import load_edf
from eegcanon.io.load_csv import load_csv

# Loader registry: extension -> loader function
LOADER_REGISTRY = {
    ".edf": load_edf,
    ".csv": load_csv,
}