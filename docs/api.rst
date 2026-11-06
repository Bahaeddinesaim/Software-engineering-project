API REST et sécurité
====================

Swagger UI est disponible à http://127.0.0.1:8000/docs et le contrat OpenAPI à
/openapi.json. GET /health renvoie 200 uniquement si modèle et clé sont prêts,
sinon 503 avec model_loaded reflétant réellement le chargement.

POST /predict exige X-API-Key. La comparaison utilise secrets.compare_digest.
Clé absente ou incorrecte : 401. Authentification non configurée : 503.
Modèle absent ou corrompu : 503. Une erreur interne de prédiction produit 500
avec un message générique. Une requête invalide produit 422 sans recopier ses valeurs.

Les 19 champs explicatifs sont obligatoires ; null explicite déclenche l'imputation.
Les champs supplémentaires sont interdits. Les catégories sont strictes, les types
numériques ne sont pas convertis depuis des chaînes, tenure est entier entre 0 et
1200, MonthlyCharges entre 0 et 100000 et TotalCharges entre 0 et 100000000.
Ces plafonds sont des garde-fous de l'API, pas des limites naturelles du dataset.

Exemple complet dans examples/customer.json. PowerShell :

.. code-block:: powershell

   Invoke-RestMethod http://127.0.0.1:8000/health
   Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/predict -Headers @{'X-API-Key'=$env:TELCOGUARD_API_KEY} -ContentType 'application/json' -Body (Get-Content examples/customer.json -Raw)

Linux :

.. code-block:: bash

   curl http://127.0.0.1:8000/health
   curl -X POST http://127.0.0.1:8000/predict -H "X-API-Key: $TELCOGUARD_API_KEY" -H 'Content-Type: application/json' --data @examples/customer.json

Réponse : prediction (0/1), churn_label (No/Yes), churn_probability (0 à 1),
risk_level et model_version. Le fichier reports/example_prediction.json contient
une réponse réellement mesurée après entraînement, si la vérification a réussi.

Les journaux indiquent démarrage, disponibilité du modèle, prédictions terminées,
échecs de validation et erreurs internes ; ils ne contiennent ni clé ni payload.
En exploitation, configurer HTTPS via reverse proxy, rotation des clés, limitation
du trafic et contrôle réseau. Ces éléments ne sont pas implémentés par cette API locale.
