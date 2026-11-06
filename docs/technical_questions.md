# Questions techniques de soutenance

1. **Pourquoi FastAPI ?** Typage Pydantic, contrat OpenAPI et TestClient facilitent la validation d'une API Python et sa vérification automatisée.
2. **Pourquoi Poetry ?** Il centralise dépendances, environnement, lock et distribution du package `src/`.
3. **Pourquoi LogisticRegression ?** C'est une baseline binaire simple, rapide, interprétable et adaptée aux variables tabulaires encodées.
4. **Pourquoi Pipeline ?** Il transporte le prétraitement ajusté et le classificateur ensemble et limite les divergences entre entraînement et inférence.
5. **Qu'est-ce qu'une fuite de données ?** L'utilisation d'informations du test ou de la cible pendant l'apprentissage ; par exemple calculer les médianes sur tout le dataset.
6. **Pourquoi pytest ?** Fixtures, paramétrisation et isolation permettent de vérifier les comportements et de reproduire les erreurs.
7. **Que signifie 75 % de couverture ?** Au moins 75 % des lignes applicatives instrumentées ont été exécutées ; cela ne garantit pas la pertinence de toutes les assertions.
8. **Pourquoi Pydantic v2 ?** Il valide types, catégories et bornes avant l'inférence et publie un schéma documenté.
9. **Comment fonctionne la clé API ?** Une dépendance lit X-API-Key et compare sa valeur au secret d'environnement en temps constant. Le secret n'est pas inclus dans le code.
10. **Si le modèle manque ?** Le démarrage journalise son indisponibilité, /health renvoie 503 et /predict ne peut pas prédire.
11. **Si le payload est invalide ?** L'API répond 422 avec les chemins et types d'erreurs sans recopier les valeurs soumises.
12. **Comment GitHub Actions fonctionne-t-il ?** Push et pull_request déclenchent un runner qui installe les dépendances verrouillées puis exécute les contrôles ; un exit code non nul échoue le job.
13. **Comment installer ailleurs ?** Cloner puis `poetry install`, ou installer la wheel ; télécharger les données et entraîner le modèle séparément.
14. **Comment reproduire l'entraînement ?** Même CSV vérifié par SHA-256, Python compatible, poetry.lock, graine 42, split 80/20 et configuration enregistrée.
15. **Pourquoi stratifier ?** Pour conserver approximativement la proportion de churn dans les partitions et évaluer les deux classes.
16. **Pourquoi exclure customerID ?** C'est un identifiant sans signification prédictive générale ; il encourage mémorisation et exposition inutile.
17. **Comment traiter TotalCharges vide ?** Conversion déterministe vers NaN, puis imputation par la médiane du train dans la Pipeline.
18. **Que faire d'une catégorie inconnue ?** Les données d'entraînement et l'API la rejettent. Le transformateur ML sait l'ignorer pour rester robuste lors d'un usage interne.
19. **Pourquoi l'accuracy ne suffit-elle pas ?** Prédire toujours la classe majoritaire peut sembler performant tout en manquant tous les départs.
20. **Precision contre recall ?** Precision mesure la part de vrais churn parmi les alertes ; recall la part des churn réellement détectés.
21. **La probabilité est-elle calibrée ?** C'est predict_proba de la régression logistique, sans recalibration ni validation spécifique de calibration ; on ne revendique pas une garantie individuelle.
22. **Pourquoi joblib est-il dangereux ?** Sa désérialisation peut exécuter du code ; on charge seulement un fichier local contrôlé et jamais un upload arbitraire.
23. **Les données sont-elles sous MIT ?** Non. MIT concerne uniquement le code de TelcoGuard ; les droits du CSV nécessitent une vérification distincte.
24. **Qu'est-ce que la ROC-AUC ?** Une mesure du classement des positifs au-dessus des négatifs, indépendante d'un seuil de décision particulier.
25. **Le seuil high est-il optimal ?** Non, 0,7 est une convention pédagogique ; un seuil métier doit être validé selon les coûts sur une partition de validation.
26. **Pourquoi StandardScaler ?** Les variables numériques ont des échelles différentes ; la régularisation de la régression est plus cohérente après normalisation.
27. **Les tests nécessitent-ils le CSV IBM ?** Non, ils utilisent des fixtures identifiées comme données de tests et des appels réseau simulés. L'évaluation finale utilise le vrai CSV.
28. **Pourquoi pas un modèle plus complexe ?** L'objectif principal est le génie logiciel reproductible ; la complexité doit être justifiée par une amélioration mesurée.
29. **Cette API suffit-elle pour une exploitation publique ?** Elle fournit la base applicative ; HTTPS, rate limiting, rotation des secrets, supervision et gouvernance restent à déployer.
30. **Pourquoi séparer validation et imputation ?** La validation vérifie un contrat sans apprendre de statistiques ; l'imputation apprend ses paramètres sur le train uniquement.
