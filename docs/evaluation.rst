Résultats mesurés
=================

Expérience locale du 6 novembre 2026, Python 3.11.9, scikit-learn 1.9.1,
graine 42, données IBM : 7 043 observations dont 1 869 churn (26,54 %).
Les 11 TotalCharges manquants sont imputés dans le pipeline. La partition
d'entraînement contient 5 634 lignes ; le test tenu à l'écart en contient 1 409.

.. list-table:: Évaluation sur le test
   :header-rows: 1

   * - Mesure
     - LogisticRegression
     - DummyClassifier prior
   * - Accuracy
     - 0,805536
     - 0,734564
   * - Precision
     - 0,657233
     - 0
   * - Recall
     - 0,558824
     - 0
   * - F1
     - 0,604046
     - 0
   * - ROC-AUC
     - 0,841861
     - 0,5

Matrice de confusion : TN = 926, FP = 109, FN = 165, TP = 209.
Le recall indique qu'environ 44 % des churn du test restent manqués au seuil 0,5.
La baseline améliore le classement et la détection par rapport au modèle constant,
mais ces mesures ne garantissent ni généralisation future ni équité entre groupes.

L'exemple examples/customer.json retourne une probabilité estimée de
0,6128185504551916, prediction 1, churn_label Yes et risque medium dans cette
expérience. Les valeurs peuvent varier si données, dépendances ou environnement
changent. Les versions et l'empreinte exactes sont conservées ci-dessous.

.. literalinclude:: ../reports/evaluation.json
   :language: json
