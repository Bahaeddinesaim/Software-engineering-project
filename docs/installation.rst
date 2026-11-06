Installation et exécution
========================================

Prérequis : Git, Python 3.11 ou 3.12 et Poetry 2.5.1.
Depuis la racine du dépôt, commandes identiques sur Linux et PowerShell :

.. code-block:: console

   python -m pip install poetry==2.5.1
   poetry install
   poetry run telcoguard download
   poetry run telcoguard prepare --output data/processed
   poetry run telcoguard eda --output reports
   poetry run telcoguard train

La première installation et le téléchargement nécessitent Internet. Les tests
n'utilisent aucun service externe. Le fichier poetry.lock fixe les dépendances.

Configuration PowerShell :

.. code-block:: powershell

   $env:TELCOGUARD_API_KEY = (poetry run python -c "import secrets; print(secrets.token_urlsafe(32))")
   poetry run uvicorn telcoguard.api.main:app --host 127.0.0.1 --port 8000

Configuration Linux :

.. code-block:: bash

   export TELCOGUARD_API_KEY="$(poetry run python -c 'import secrets; print(secrets.token_urlsafe(32))')"
   poetry run uvicorn telcoguard.api.main:app --host 127.0.0.1 --port 8000

Une clé d'au moins 32 caractères est obligatoire. Une variable d'environnement
est prioritaire sur .env. Le modèle est lu depuis models/pipeline.joblib ;
TELCOGUARD_MODEL_PATH permet de changer ce chemin. Les chemins relatifs sont
résolus depuis le répertoire de lancement. Ne versionnez jamais .env.

Distribution à une autre équipe :

.. code-block:: console

   poetry build
   python -m venv fresh
   fresh/Scripts/python -m pip install dist/telcoguard_ai-1.0.0-py3-none-any.whl

Sur Linux, remplacer fresh/Scripts/python par fresh/bin/python. La roue contient
le package, pas les données ni le modèle : télécharger puis entraîner séparément.
