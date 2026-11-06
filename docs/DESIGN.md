# Direction visuelle — TelcoGuard

**Intention :** un outil d'analyse calme et distinctif, construit autour de la relation
client et de signaux lisibles. Référence interne : données et tâches du projet.

**Couleurs :** fond #f6f7fb, surfaces blanches, navigation #14283f, texte #172b42,
texte secondaire #718096, traits #e5e9f0, accent corail #e57850. Le vert indique la
disponibilité ; le risque ajoute toujours un libellé, pas seulement une couleur.

**Typographie :** Segoe UI/Arial pour les éléments HTML ; typographie sans serif
native Streamlit pour les widgets. Titres 32–49 px, corps 13–14 px, nombres de
synthèse 29 px et score 62 px. Valeurs alignées et unités explicites.

**Géométrie :** navigation latérale, grille principale jusqu'à 1440 px, espaces de
8/12/16/24 px, surfaces bordées de 12 px de rayon sans ombres lourdes. Les cartes
encadrent les métriques ou les outils ; le texte pédagogique reste simple.

**Composants :** navigation sélectionnée sur fond bleu clair, actions principales
corail, formulaire en deux sections, résultat à droite avec jauge et export,
graphiques Plotly cohérents en encre/corail/vert. SVG locaux intégrés comme images,
sans ressources externes ni photographie décorative.

**Adaptation :** colonnes empilées sur mobile, navigation rétractable, tableau dans
une région défilante. Les animations respectent prefers-reduced-motion. Focus
visible, contrôles natifs clavier, labels persistants et détails textuels des risques.

**Preuves visuelles :** captures du navigateur réel dans reports/ui à 1440 px et
390 px ; vérifier aussi le simulateur après soumission et les états de chargement.
