Développement, limites et dépannage
===================================

Installer les hooks avec poetry run pre-commit install. La configuration Ruff
couvre erreurs Python, imports, modernisation, pièges courants et formatage.
Les fonctions gardent des responsabilités séparées et des docstrings en anglais.

Une réponse 503 demande de vérifier models/pipeline.joblib, l'environnement actif,
la clé et le répertoire courant. Un échec de chargement peut venir d'une corruption
ou de versions incompatibles : réentraîner avec poetry.lock plutôt que charger
un modèle non fiable. Une erreur 422 indique un contrat non respecté ; consulter
Swagger, utiliser les catégories exactes et des nombres JSON.

Un échec réseau du téléchargement ne crée pas de faux CSV. Vérifier DNS, proxy et
accès au domaine raw.githubusercontent.com puis relancer la commande. Ne pas
désactiver la vérification TLS. Un changement de schéma entraîne un rejet explicite.

Limites : données pédagogiques historiques, licence des données à clarifier,
absence de calibration dédiée, audit d'équité, validation temporelle et surveillance
de drift. Le secret partagé n'offre pas d'identités individuelles. Aucun débit
limite, chiffrement TLS natif ou gestion de secrets distante n'est fourni.

Améliorations : validation prospective, calibration sur validation séparée,
choix du seuil selon les coûts métier, tests d'équité, observabilité et rotation
des modèles. Éviter d'optimiser répétitivement sur le même test final.

Usage de l'IA : code, tests et documentation ont été rédigés avec l'assistance de
Codex. Les résultats annoncés doivent provenir des commandes exécutées. L'auteur
reste responsable de la compréhension, de la revue et de la soutenance.
