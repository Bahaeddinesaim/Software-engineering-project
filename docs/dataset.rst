Provenance et qualité des données
========================================

Source : `dépôt IBM <https://github.com/IBM/telco-customer-churn-on-icp4d>`_,
Code Pattern pédagogique utilisant Cloud Pak for Data et Watson Machine Learning.
Le `CSV original <https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv>`_
est téléchargé par notre script Python ; aucune donnée synthétique ne remplace
les observations d'entraînement. Les fixtures de tests sont artificielles et isolées.

Le dépôt IBM affiche Apache-2.0 pour le dépôt logiciel. Aucune attribution
automatique de cette licence au CSV n'est faite ici. Les pages consultées ne
fournissent pas de licence spécifique au jeu de données clairement distincte.
Les droits de réutilisation et de redistribution des données doivent donc être
clarifiés avant tout autre usage ; la licence MIT de ce projet concerne seulement
notre code. Le CSV et les artefacts entraînés sont ignorés par Git.

Le schéma attendu comporte 21 colonnes, dont customerID et la cible Churn.
Le téléchargement produit un manifeste avec URL, SHA-256, dimensions et colonnes.
La branche master peut évoluer : conserver le manifeste et comparer son empreinte
pour reproduire exactement une expérience. Le téléchargement existant est validé
et réutilisé ; --force le renouvelle. Trois tentatives et un timeout de 30 secondes
gèrent les erreurs HTTP. Le contenu est validé avant remplacement du fichier.

Les chaînes vides deviennent des valeurs manquantes ; TotalCharges est converti
en nombre, mais un texte non numérique est rejeté. Les doublons exacts sont supprimés.
Des identifiants manquants ou contradictoires sont rejetés pour éviter qu'un même
client traverse les deux partitions. Les catégories inattendues dans les données
d'entraînement, cibles invalides, valeurs infinies et nombres négatifs sont rejetés.
Les variables explicatives manquantes sont conservées jusqu'à l'imputation.

Le dataset est un exemple pédagogique sans garantie de représentativité d'un
opérateur actuel. L'absence de dimension temporelle exploitable empêche une vraie
validation prospective. La présence de variables démographiques impose une étude
d'équité avant utilisation métier. customerID ne participe ni au modèle ni à l'API.
