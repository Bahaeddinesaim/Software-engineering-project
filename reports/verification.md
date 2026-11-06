# Rapport de livraison — TelcoGuard AI

Vérifications locales du **6 novembre 2026**, Windows, Python 3.11.9.
Auteur : SAIM Bahaeddine — EPITA, SOENFO, année 2026–2027.
Le dépôt initial ne contenait que `.git` ; aucun PDF officiel n'était disponible.

Statuts : **PASS** = exécuté et vérifié ; **FAIL** = échec constaté ;
**NOT RUN** = non exécuté ; **BLOCKED** = dépendance identifiée empêchant l'action.

## Architecture et fonctionnalités

Package installable `src/telcoguard` : `data` (HTTP, schéma, nettoyage), `ml`
(prétraitement, entraînement, évaluation et inférence), `api` (contrats, sécurité,
routes et lifecycle), `config` et CLI. Scripts réutilisables, notebook EDA exécuté,
tests unitaires/intégration/API, rapports et documentation Sphinx en français.

Acquisition avec timeout, retries et contrôle de cache ; nettoyage déterministe ;
split stratifié 80/20 ; imputation et encodage ajustés uniquement sur le train ;
régression logistique ; comparaison DummyClassifier ; persistance joblib et JSON.
L'API valide 19 features, protège POST /predict par clé d'environnement,
masque les données dans ses erreurs et journalise les événements sans payload.
Une clé non configurée ou un modèle indisponible empêche un statut de disponibilité.

## Dataset réel et performances

Source : [CSV du dépôt IBM](https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv),
référencé par le [Code Pattern IBM](https://github.com/IBM/telco-customer-churn-on-icp4d).
Réponse HTTP 200 obtenue via notre script Python : **7 043 lignes, 21 colonnes**.
Classes : 5 174 No et 1 869 Yes. TotalCharges : 11 valeurs manquantes.
`customerID` est exclu de l'apprentissage et des requêtes d'inférence.

SHA-256 : `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91`.
Le manifeste conservé dans `reports/dataset_source.json` permet la comparaison.

Entraînement : 5 634 lignes ; test : 1 409 lignes ; graine : 42.
Versions mesurées : Python 3.11.9 et scikit-learn 1.9.1.

| Mesure | LogisticRegression | DummyClassifier prior |
|---|---:|---:|
| Accuracy | 0,805536 | 0,734564 |
| Precision | 0,657233 | 0 |
| Recall | 0,558824 | 0 |
| F1 | 0,604046 | 0 |
| ROC-AUC | 0,841861 | 0,5 |

Matrice de confusion, lignes vérité et colonnes prédiction, ordre [No, Yes] :
`[[926, 109], [165, 209]]`. Les résultats complets sont dans `reports/evaluation.json`
et `models/metadata.json`. Le score est une estimation logistique non recalibrée.
Le seuil de décision est 0,5 ; les bornes des risques sont 0,3 et 0,7.

La requête `examples/customer.json` produit réellement :

```json
{
  "prediction": 1,
  "churn_label": "Yes",
  "churn_probability": 0.6128185504551916,
  "risk_level": "medium",
  "model_version": "1.0.0"
}
```

## Checklist des exigences académiques

| Exigence | Statut | Preuve et portée |
|---|---|---|
| Téléchargement réel reproductible | PASS | CLI download, HTTP 200, manifeste SHA-256 |
| Validation du schéma et nettoyage | PASS | 21 colonnes réelles, tests valeurs/catégories/doublons |
| EDA | PASS | `reports/eda.json`, notebook exécuté avec sorties agrégées |
| Split et prévention de fuite | PASS | Pipeline fit sur train, test comparant médianes au train |
| Entraînement, métriques et baseline | PASS | `reports/evaluation.json`, chiffres ci-dessus |
| Sérialisation et rechargement | PASS | joblib local, tests round trip et reproductibilité |
| API réelle et Swagger | PASS | Uvicorn subprocess et requêtes HTTP, `reports/live_api.json` |
| GET /health et POST /predict | PASS | 200 / 200 avec modèle et clé prêts |
| Sécurité et validation | PASS | 401 sans clé et mauvaise clé, 422 payload invalide ; tests 503/500 |
| Tests automatisés | PASS | **44 tests réussis**, dont trois parcours Streamlit ; `reports/checks/pytest.log` |
| Couverture ≥ 75 % | PASS | **97,15 %**, 579 lignes exécutées sur 596 ; `htmlcov/index.html` |
| Ruff lint et format | PASS | contrôles finaux sans erreur, logs `reports/checks/` |
| Poetry et lock | PASS | `poetry check --lock --strict`, `poetry.lock` généré |
| Package wheel et sdist | PASS | `dist/telcoguard_ai-1.0.0-py3-none-any.whl` et `.tar.gz` |
| Installation en environnement vierge | PASS | `.venv-package`, import depuis site-packages, prédiction et API HTTP |
| Sphinx français et autodoc | PASS | build avec `-W`, `docs/_build/html/index.html` |
| CI présente et structure validée | PASS | YAML parsé, triggers/matrice/commandes vérifiés localement |
| GitHub Actions distant | NOT RUN | aucun push ni lancement distant effectué |
| Python 3.12 en local | NOT RUN | vérifications exécutées avec Python 3.11 ; 3.12 déclaré en CI |
| README, installation Windows/Linux | PASS | commandes complètes, exemples JSON, sécurité et limites |
| Soutenance et questions | PASS | plan de 20 minutes et 30 questions/réponses |
| Plateforme Streamlit | PASS | quatre vues, prédiction locale, filtres, export, captures ordinateur/mobile |
| Secrets et données exclus de Git | PASS | `.env`, CSV, modèles et environnements ignorés ; clé de smoke test éphémère non écrite |

Les journaux des contrôles et codes de sortie sont dans `reports/checks/` et
`reports/checks.json`. Les premières erreurs réseau d'environnement, un mock de
probabilité mal typé, la cellule SVG du notebook et les titres RST ont été corrigés,
puis les contrôles concernés relancés avec succès. Les avertissements du runtime
Jupyter Windows n'ont pas empêché l'exécution complète du notebook.

## Démarrage et démonstration dans cet espace de travail

PowerShell, depuis la racine (Poetry est installé dans `.venv`) :

```powershell
.\.venv\Scripts\poetry run telcoguard download
.\.venv\Scripts\poetry run telcoguard train
$env:TELCOGUARD_API_KEY = (.\.venv\Scripts\python -c "import secrets; print(secrets.token_urlsafe(32))")
.\.venv\Scripts\poetry run uvicorn telcoguard.api.main:app --host 127.0.0.1 --port 8000
```

Ouvrir `http://127.0.0.1:8000/docs`, cliquer Authorize et utiliser la clé privée.
Pour une démonstration automatisée sans afficher de secret :

```powershell
.\.venv\Scripts\poetry run python scripts/verify_live_api.py
.\.venv\Scripts\poetry run python scripts/validate_project.py
```

Le smoke test démarre son propre serveur, réalise health, prédiction, rejets de
clés et validation, puis arrête uniquement ce processus. Aucun serveur ne reste
en cours après la vérification. Pour un clone neuf, suivre le README et `poetry install`.

## Limites restantes

La licence spécifique du CSV n'a pas été établie distinctement dans les pages IBM
consultées ; Apache-2.0 du dépôt ne lui est pas automatiquement attribuée. Clarifier
les droits avant redistribution ou exploitation. La licence MIT porte sur notre code.

Le dataset pédagogique ne garantit ni représentativité actuelle, ni absence de
biais. Calibration dédiée, validation temporelle, audit d'équité, HTTPS, rate limiting,
rotation des secrets et monitoring restent des travaux d'exploitation. La couverture
de lignes élevée ne constitue pas une preuve de correction exhaustive.
Aucune réussite de CI distante ou de déploiement n'est revendiquée.
