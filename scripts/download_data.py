"""Download the IBM dataset using the installed package."""

from pathlib import Path

from telcoguard.data.loader import download_data

if __name__ == "__main__":
    download_data(Path("data/raw/telco.csv"))
