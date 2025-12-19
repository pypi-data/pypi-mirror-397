import urllib.request
from pathlib import Path

# URLs for UNSW-NB15 CSV files (commonly used for testing)
# These are hosted on multiple sites, UNWS's main link is a web page, 
# but the raw CSVs are often at specific researchers' paths or GitHub mirrors.
# Kaggle/GitHub mirrors are more reliable for direct download.
UNSW_TEST_URL = "https://raw.githubusercontent.com/Nir-J/ML-Projects/master/UNSW-Network_Packet_Classification/UNSW_NB15_testing-set.csv"
UNSW_TRAIN_URL = "https://raw.githubusercontent.com/Nir-J/ML-Projects/master/UNSW-Network_Packet_Classification/UNSW_NB15_training-set.csv"

BENCHMARKS_DIR = Path("m:/workspace/moa_telehealth_governor/benchmarks")
BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)

def download_unsw():
    test_path = BENCHMARKS_DIR / "UNSW_NB15_testing-set.csv"
    if not test_path.exists():
        print(f"Downloading UNSW-NB15 testing set from {UNSW_TEST_URL}...")
        urllib.request.urlretrieve(UNSW_TEST_URL, test_path)
        print(f"Downloaded to {test_path}")
    else:
        print(f"UNSW-NB15 testing set already exists at {test_path}")

    train_path = BENCHMARKS_DIR / "UNSW_NB15_training-set.csv"
    if not train_path.exists():
        print(f"Downloading UNSW-NB15 training set from {UNSW_TRAIN_URL}...")
        urllib.request.urlretrieve(UNSW_TRAIN_URL, train_path)
        print(f"Downloaded to {train_path}")
    else:
        print(f"UNSW-NB15 training set already exists at {train_path}")

if __name__ == "__main__":
    download_unsw()
