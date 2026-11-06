"""Create a portable EDA notebook with no embedded customer identifiers."""

import json
from pathlib import Path


def main() -> None:
    """Write a notebook using standard notebook JSON and deterministic cells."""
    sources = [
        (
            "markdown",
            "# Exploration IBM Telco\n"
            "SAIM Bahaeddine — SOENFO 2026–2027. Exécuter depuis notebooks/ ou la racine.\n"
            "Les données sont acquises séparément avec `poetry run telcoguard download`.\n"
            "L'EDA ne modifie pas le pipeline ; aucun identifiant individuel n'est affiché.",
        ),
        (
            "code",
            "from pathlib import Path\nimport pandas as pd\n"
            "from telcoguard.data.validation import validate_dataset\n"
            "root = Path.cwd() if Path('data/raw/telco.csv').exists() else Path.cwd().parent\n"
            "df = validate_dataset(pd.read_csv(root / 'data/raw/telco.csv'))\n"
            "print(f'Dimensions : {df.shape}')\n"
            "print(df.drop(columns='customerID').dtypes.to_string())",
        ),
        (
            "code",
            "print('Valeurs manquantes :')\n"
            "print(df.isna().sum().to_string())\n"
            "print('Distribution du churn :')\nprint(df.Churn.value_counts().to_string())\n"
            "print(df.Churn.value_counts(normalize=True).to_string())",
        ),
        (
            "code",
            "print(df.describe().to_string())\n"
            "print(pd.crosstab(df.Contract, df.Churn, normalize='index').to_string())\n"
            "print(pd.crosstab(df.InternetService, df.Churn, normalize='index').to_string())",
        ),
        (
            "code",
            """from IPython.display import SVG, display
counts = df.Churn.value_counts()
bars = ""
for i, (label, count) in enumerate(counts.items()):
    x = 40 + i * 180
    height = count / 25
    bars += (
        f'<rect x="{x}" y="{250-height}" width="100" height="{height}" fill="#2563eb"/>'
        f'<text x="{x}" y="275">{label}: {count}</text>'
    )
display(SVG(f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="300">{bars}</svg>'))
""",
        ),
        (
            "markdown",
            "## Interprétation et limites\n"
            "Comparer proportions, valeurs manquantes et contrats. Une association observée "
            "n'est pas causale. Le déséquilibre justifie precision, recall, F1 et ROC-AUC "
            "en complément de l'accuracy. Ne pas choisir un seuil après consultation répétée "
            "du test final. Les données pédagogiques ne garantissent pas la représentativité.",
        ),
    ]
    cells = []
    for index, (kind, source) in enumerate(sources):
        cell = {
            "cell_type": kind,
            "id": f"eda-{index}",
            "metadata": {},
            "source": source.splitlines(keepends=True),
        }
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}
        },
    }
    path = Path("notebooks/exploratory_analysis.ipynb")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
