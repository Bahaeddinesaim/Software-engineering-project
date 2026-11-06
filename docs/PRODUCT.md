# Produit — plateforme de démonstration

**Public :** équipe du projet, jury SOENFO et lecteurs. Objectif : démontrer
l'exploration, l'inférence et la qualité de la baseline dans une soutenance.
La plateforme locale fonctionne sur ordinateur et reste utilisable sur mobile.

**Parcours :** vue d'ensemble → simulation d'un profil hypothétique → exploration
d'une cohorte → lecture des preuves du modèle. Le simulateur utilise les 19 features
de `Customer` et la Pipeline locale. L'API FastAPI conserve son authentification.
Streamlit, lié à 127.0.0.1, n'a pas d'authentification propre.

**Vérité du contenu :** statistiques du CSV IBM validé, scores issus de predict_proba,
métriques du modèle chargé ou rapport existant si absent. Aucun client inventé ni
promesse de rétention ; scénarios explicitement hypothétiques. Montants sans unité
européenne inventée. Identifiants exclus des affichages.

**Contrats :** navigation à quatre vues, clé de widget `navigation`, point d'entrée
`streamlit_app.py`, scénario réinitialisant le résultat, téléchargement JSON du score
et du profil réellement analysé. Les états sans modèle, sans données et sans
résultat de filtre doivent rester explicites.

**Voix :** français clair, professionnel, pédagogique. Distinguer observation et
prédiction, expliquer le risque, ne pas revendiquer de calibration ni de causalité.
