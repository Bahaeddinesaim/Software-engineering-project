# Soutenance TelcoGuard AI — 20 minutes

Préparation : installer avec `poetry install`, télécharger, entraîner et configurer une clé privée. Ouvrir le terminal, Swagger, `htmlcov/index.html`, la documentation Sphinx et `reports/verification.md`. Ne jamais projeter la clé ou un fichier `.env`.

| Temps | Contenu et démonstration |
|---|---|
| 00:00–02:00 | Présenter SOENFO, EPITA, SAIM Bahaeddine et le besoin de fidélisation. Distinguer prédiction statistique et efficacité causale d'une campagne. |
| 02:00–04:00 | Expliquer IBM, dimensions mesurées, cible déséquilibrée et ambiguïté des droits du CSV. Montrer le manifeste SHA-256, sans afficher les identifiants. |
| 04:00–06:00 | Parcourir `src/telcoguard` : data, ml, api et config. Montrer le flux acquisition → validation → split → Pipeline → artefact → API. |
| 06:00–08:00 | Expliquer TotalCharges vide, doublons, catégories, médiane, OneHotEncoder et StandardScaler. Insister sur fit exclusivement après le split. |
| 08:00–10:00 | Exécuter `poetry run telcoguard train`. Lire les résultats réellement présents dans metadata.json : accuracy, precision, recall, F1, ROC-AUC et matrice. Comparer au DummyClassifier. |
| 10:00–13:00 | Lancer Uvicorn et GET /health. Dans Swagger, autoriser via X-API-Key, utiliser `examples/customer.json`, puis montrer une prédiction. Expliquer le seuil 0,5, les risques 0,3/0,7 et l'absence de calibration dédiée. |
| 13:00–14:00 | Montrer 401 sans clé, 422 avec tenure négatif et 503 dans les tests d'artefact absent. Éviter de supprimer le vrai modèle pour la démo. |
| 14:00–16:00 | Exécuter `poetry run pytest`, expliquer fixtures hors réseau et tests unitaires/intégration/API. Ouvrir la couverture HTML et interpréter les lignes non couvertes. |
| 16:00–17:00 | Exécuter Ruff, `poetry build` et montrer wheel/sdist. Expliquer comment une autre équipe installe le package. |
| 17:00–18:00 | Construire Sphinx et parcourir installation, API et référence autodoc. |
| 18:00–19:00 | Montrer le YAML GitHub Actions : Python 3.11/3.12, lock, Ruff, couverture, build et documentation. Distinguer validation locale et exécution distante effectivement observée. |
| 19:00–20:00 | Conclure sur reproductibilité, sécurité et limites : représentativité, droits, équité, calibration, validation temporelle et protection du service. Mentionner l'assistance IA et la revue de l'auteur. |

Si Internet est indisponible, utiliser le CSV déjà validé et le modèle local ; les tests restent exécutables. Si l'entraînement échoue, expliquer l'erreur réellement observée plutôt que présenter des chiffres inventés.
