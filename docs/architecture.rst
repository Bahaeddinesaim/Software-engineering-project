Architecture et apprentissage
==============================

Flux : CSV IBM → validation déterministe → séparation stratifiée 80/20 → Pipeline
ajusté sur les 80 % → évaluation sur les 20 % → joblib → FastAPI.

Le package src/telcoguard sépare data (acquisition/validation), ml
(prétraitement/entraînement/évaluation/inférence), api (contrats/routes/sécurité)
et config (pydantic-settings). La CLI et les scripts appellent ces mêmes services.
Les dépendances incluent pandas, NumPy, scikit-learn, FastAPI, Pydantic v2,
Uvicorn, joblib et httpx ; Poetry gère installation et packaging.

Le ColumnTransformer traite quatre variables numériques : SeniorCitizen, tenure,
MonthlyCharges et TotalCharges. SimpleImputer utilise la médiane et StandardScaler
met les échelles en cohérence. Les 15 variables catégorielles utilisent l'imputation
par modalité majoritaire puis OneHotEncoder(handle_unknown='ignore'). Le pipeline
tolère ainsi une modalité inconnue au niveau ML ; l'API conserve un contrat strict.

LogisticRegression est une référence simple et interprétable. La graine 42 fixe
le split stratifié. Les médianes, modalités, échelles et coefficients sont appris
exclusivement sur l'entraînement. Il n'y a pas de recherche d'hyperparamètres.
Le nettoyage du schéma n'apprend aucune statistique. Le seuil de classification
vaut 0,5 ; TELCOGUARD_THRESHOLD permet un seuil d'exploitation différent.

Le modèle retourne predict_proba : estimation logistique non recalibrée, sans
garantie individuelle. Les niveaux low (< 0,3), medium (0,3 à < 0,7) et high
(≥ 0,7) sont des conventions pédagogiques, indépendantes du seuil de classification.

metadata.json contient versions, empreinte des données, configuration, schéma,
effectifs, distribution de classe, accuracy, precision, recall, F1, ROC-AUC et matrice
de confusion. Les lignes de la matrice représentent la vérité [No, Yes], les colonnes
la prédiction [No, Yes]. Un DummyClassifier prior fournit un point de comparaison.
L'accuracy masque les erreurs sur la classe minoritaire ; recall et precision
éclairent les coûts d'un client perdu et d'une campagne inutile. La ROC-AUC compare
le classement sans imposer de seuil. Aucun résultat n'est déduit des seules fixtures.

joblib peut exécuter du code à la désérialisation. Seuls les artefacts locaux
contrôlés par l'opérateur sont autorisés ; aucun endpoint n'accepte de modèle.
