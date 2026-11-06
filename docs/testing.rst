Tests et assurance qualité
========================================

.. code-block:: console

   poetry run ruff check .
   poetry run ruff format --check .
   poetry run pytest --cov=telcoguard --cov-report=term-missing --cov-report=html --cov-fail-under=75
   poetry build
   poetry run sphinx-build -W -b html docs docs/_build/html

Les tests unitaires vérifient schéma, nettoyage, encodage, prétraitement, catégories
inconnues, configuration et acquisition simulée. Les tests d'intégration entraînent
un estimateur temporaire, vérifient persistance, rechargement et reproductibilité.
Les tests API couvrent succès, validation, authentification, modèle absent et erreur
interne contrôlée. Les fixtures déterministes ne nécessitent ni réseau ni secret réel.

La couverture mesure les lignes exécutées, pas l'absence de bugs ; pytest impose
75 % sur tous les modules applicatifs. htmlcov/index.html détaille les lignes
restantes. Les assertions vérifient les comportements ; elles ne sont pas de simples
captures des valeurs courantes d'une implémentation.

La CI .github/workflows/ci.yml s'exécute sur push et pull_request avec Python 3.11
et 3.12 : installation verrouillée, Ruff, pytest et couverture, Poetry build et
Sphinx avec avertissements bloquants. Les rapports sont publiés comme artefacts.
Aucun déploiement automatique n'est configuré. La réussite locale ne prouve pas
la réussite distante ; consulter Actions après un push explicitement autorisé.
