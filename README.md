# TelcoGuard AI — Customer Churn Prediction API

Application Python de prédiction du départ des clients télécom : acquisition réelle,
validation, entraînement reproductible, API authentifiée et vérification automatisée.
Elle illustre une démarche de Software Engineering for Data autour d'une baseline
interprétable, avec séparation entre données, apprentissage et service REST.

**Contexte académique :** MSc Informatique & Management, spécialisation Data, EPITA,
SOENFO, année 2026–2027. Enseignante : Dr. Nour El Houda Ben Chaabene.
**Auteur : SAIM Bahaeddine ; Hazem OUNI** Projet de groupe.

## Besoin métier et données

Estimer le risque de churn aide à prioriser les actions de fidélisation. Une prédiction
ne démontre pas qu'une action marketing empêchera le départ d'un client.

Le [CSV IBM](https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv)
provient du [Code Pattern Cloud Pak for Data](https://github.com/IBM/telco-customer-churn-on-icp4d).
Il contient 7 043 lignes et 21 colonnes, dont la cible `Churn`. Le manifeste créé au
téléchargement enregistre dimensions, colonnes, URL et SHA-256. `customerID` est exclu
de l'apprentissage et de l'API. Les données brutes et modèles ne sont pas versionnés.

Le dépôt IBM affiche Apache-2.0 pour son logiciel ; les documents consultés ne
clarifient pas une licence distincte pour le CSV. **Ne pas attribuer automatiquement
cette licence au dataset.** Clarifier les droits avant redistribution ou usage métier.
Notre [licence MIT](LICENSE) concerne uniquement le code et la documentation TelcoGuard.

## Architecture et stack

```text
CSV IBM → validation → split stratifié 80/20 → Pipeline → métriques + joblib
                                                           ↓
                                  X-API-Key → FastAPI → prédiction
src/telcoguard/
  data/    acquisition, contrôle du schéma et nettoyage déterministe
  ml/      preprocessing, training, evaluation, inference
  api/     schémas Pydantic, dépendances de sécurité, routes, lifecycle
  config.py  environnement et secrets
tests/     unit, integration, api
docs/      Sphinx, soutenance et questions techniques
```

Python 3.11/3.12, Poetry, pandas, NumPy, scikit-learn, FastAPI, Pydantic v2,
pydantic-settings, Uvicorn, joblib, httpx, pytest, pytest-cov, Ruff, pre-commit,
Sphinx et GitHub Actions. Les dépendances exactes sont dans `poetry.lock`.

## Installation et entraînement

Depuis la racine du dépôt, sur Windows PowerShell ou Linux :

```console
python -m pip install poetry==2.5.1
poetry install
poetry run telcoguard download
poetry run telcoguard prepare --output data/processed
poetry run telcoguard eda --output reports
poetry run telcoguard train
```

Les scripts `scripts/download_data.py`, `prepare_data.py` et `train_model.py`
fournissent aussi des points d'entrée via `poetry run python scripts/<nom>.py`.
Le notebook `notebooks/exploratory_analysis.ipynb` explore les mêmes données.

`models/pipeline.joblib` contient l'ensemble du prétraitement ajusté et du modèle.
`models/metadata.json` décrit schéma, configuration, versions et résultats réellement
mesurés. Médiane, normalisation et OneHotEncoder sont ajustés uniquement sur le train.
La régression logistique utilise un split stratifié avec graine 42, sans tuning.
Les métriques du test sont comparées à un DummyClassifier : accuracy, precision,
recall, F1, ROC-AUC et matrice [No, Yes]. L'accuracy seule masque la classe minoritaire.

Mesures locales du 6 novembre 2026, sur **1 409 lignes de test** :

| Modèle | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| LogisticRegression | 0,805536 | 0,657233 | 0,558824 | 0,604046 | 0,841861 |
| DummyClassifier prior | 0,734564 | 0 | 0 | 0 | 0,5 |

Matrice : `[[926, 109], [165, 209]]`. Voir [les résultats et leur provenance](reports/evaluation.json).

## Configuration et API

Générer une clé privée de 32 caractères minimum, sans la publier. `.env.example`
liste les variables disponibles ; `.env` est ignoré. PowerShell :

```powershell
$env:TELCOGUARD_API_KEY = (poetry run python -c "import secrets; print(secrets.token_urlsafe(32))")
poetry run uvicorn telcoguard.api.main:app --host 127.0.0.1 --port 8000
```

Linux :

```bash
export TELCOGUARD_API_KEY="$(poetry run python -c 'import secrets; print(secrets.token_urlsafe(32))')"
poetry run uvicorn telcoguard.api.main:app --host 127.0.0.1 --port 8000
```

Swagger : <http://127.0.0.1:8000/docs> ; OpenAPI : `/openapi.json`.
Dans Swagger, cliquer **Authorize** puis saisir la clé sans préfixe Bearer.

| Endpoint | Contrat |
|---|---|
| `GET /health` | 200 si modèle et authentification prêts ; sinon 503 |
| `POST /predict` | 19 features, header `X-API-Key`, réponse de risque |

Exemple de requête réaliste, sans identifiant : [examples/customer.json](examples/customer.json).
PowerShell, dans un deuxième terminal avec la même clé :

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -Headers @{'X-API-Key'=$env:TELCOGUARD_API_KEY} -ContentType 'application/json' -Body (Get-Content examples/customer.json -Raw)
```

Linux :

```bash
curl -X POST http://127.0.0.1:8000/predict -H "X-API-Key: $TELCOGUARD_API_KEY" -H 'Content-Type: application/json' --data @examples/customer.json
```

Exemple de **structure** de réponse (chiffres illustratifs, pas une mesure) :

```json
{"prediction": 1, "churn_label": "Yes", "churn_probability": 0.78, "risk_level": "high", "model_version": "1.0.0"}
```

La réponse réellement mesurée est enregistrée dans `reports/example_prediction.json`.
Le seuil de décision vaut 0,5. Risques : low < 0,3 ; medium de 0,3 à < 0,7 ; high ≥ 0,7.
Il s'agit d'estimations `predict_proba` non recalibrées, sans garantie individuelle.

Tous les champs sont requis ; `null` explicite permet l'imputation. Valeur incorrecte,
champ absent ou supplémentaire : 422. Clé absente/incorrecte : 401. Modèle absent
ou authentification non configurée : 503. Erreur interne : 500 générique.
Les logs ne contiennent ni payload ni secret. Seuls les modèles locaux contrôlés
sont chargés : joblib ne doit jamais désérialiser un upload non fiable.

## Tests, qualité et packaging

```console
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest --cov=telcoguard --cov-report=term-missing --cov-report=html --cov-fail-under=75
poetry build
poetry run sphinx-build -W -b html docs docs/_build/html
poetry run pre-commit install
```

Les tests utilisent des fixtures temporaires et des mocks HTTP, sans téléchargement
ni secret réel. `htmlcov/index.html` détaille la couverture ; le seuil bloquant est
75 %. La couverture mesure des lignes exécutées et ne prouve pas l'absence de défauts.
Voir [reports/verification.md](reports/verification.md) pour les résultats constatés.
Sphinx génère `docs/_build/html/index.html` et la référence autodoc.

Une autre équipe peut installer `dist/telcoguard_ai-1.0.0-py3-none-any.whl` dans un
environnement Python vierge, puis télécharger et entraîner via la CLI. Le package
n'embarque pas les données, le secret ni le modèle. Voir la documentation d'installation.

## CI/CD et présentation

La [CI](.github/workflows/ci.yml) s'exécute sur push et pull_request pour Python 3.11
et 3.12 : dépendances verrouillées, Ruff, pytest ≥ 75 %, build Poetry et Sphinx.
Elle archive rapports et distributions. Aucun déploiement automatique n'est prévu.
**Une validation locale ne signifie pas qu'une exécution GitHub distante a réussi.**
Aucun push n'est réalisé sans autorisation explicite.

- [Plan de soutenance, 20 minutes](docs/demo_script.md)
- [30 questions techniques avec réponses](docs/technical_questions.md)
- [Documentation Sphinx](docs/index.rst)

## Limites et transparence

Données pédagogiques historiques, représentativité limitée, licence du CSV à
clarifier, absence de calibration dédiée, d'audit d'équité et de validation temporelle.
Pour un service public : ajouter HTTPS, rate limiting, supervision, rotation des
clés et gouvernance des modèles. Les plafonds numériques de l'API sont des garde-fous.
Les suites envisageables sont calibration, seuils fondés sur les coûts métier,
validation prospective et surveillance du drift.

**Usage de l'IA :** Codex a assisté la rédaction du code, des tests et de la
documentation. Les résultats présentés proviennent des commandes exécutées ;
l'auteur reste responsable de la revue, de la compréhension et de la soutenance.
# Software-engineering-project
