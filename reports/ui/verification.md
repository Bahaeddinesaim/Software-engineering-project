# Vérification de la plateforme Streamlit

Vérification locale du 6 novembre 2026, Streamlit 1.67.0 et Plotly 6.9.0.

| Contrôle | Résultat |
|---|---|
| Quatre vues et navigation | PASS |
| Prédiction réelle via le formulaire | PASS |
| Changement de scénario et invalidation du résultat | PASS — AppTest |
| Exploration filtrée et sélection vide | PASS — AppTest |
| États sans modèle ou sans données | PASS — AppTest |
| Rendu Chrome ordinateur 1440 px | PASS — captures ci-dessous |
| Rendu Chrome mobile 390 px | PASS — captures ci-dessous |
| Chargement des illustrations locales | PASS — contrôle naturalWidth dans Chrome |
| Erreurs JavaScript de page | PASS — aucune détectée |
| Débordement horizontal de la page mobile | PASS — aucun détecté |
| Suite complète | PASS — 48 tests, couverture 97,12 % |
| Ruff, Poetry, Sphinx | PASS — journaux dans reports/checks |
| GitHub Actions distant | NOT RUN |

Captures : overview-desktop.png, simulator-desktop.png, explorer-desktop.png,
model-desktop.png, overview-mobile.png et overview-mobile-detail.png.
Les screenshots montrent le CSV IBM et les estimations du modèle local ; les profils
de simulation sont des exemples hypothétiques. Aucun identifiant client n'est affiché.

Le tableau HTML évite une dépendance d'affichage à la DLL PyArrow bloquée par le
contrôle d'application Windows de cette machine. L'aperçu reste limité à 100 lignes,
et les agrégations portent sur toute la sélection. Aucun contrôle Windows n'a été désactivé.

Les contrôles visuels ne constituent pas un audit complet WCAG. L'API protégée
reste séparée ; Streamlit fonctionne localement sans authentification propre.
