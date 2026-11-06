"""Train and persist the baseline from the downloaded IBM CSV."""

from pathlib import Path

from telcoguard.ml.training import train

if __name__ == "__main__":
    print(train(Path("data/raw/telco.csv"), Path("models")))
