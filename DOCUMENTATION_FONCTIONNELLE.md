# Documentation Fonctionnelle de l'Application Web – Projet T'EleFan

### 1. Le concept de l'application et notre cahier des charges
Le but de notre application T'EleFan, c'était de prendre les exports de données assez bruts et illisibles de la ligne automatisée FESTO, et d'en faire un vrai outil de pilotage pour l'usine. 

Dans notre cahier des charges (la documentation analytique), on devait absolument couvrir les 4 grands piliers de la production industrielle : la performance (efficacité), la qualité, la logistique (flux) et la maintenance. Pour que ce soit super clair pour les utilisateurs, on a tout simplement découpé notre tableau de bord Streamlit en suivant exactement ces 4 axes, avec un code couleur pour chaque. L'idée c'est qu'un manager puisse voir en un coup d'œil si la ligne tourne bien ou si ça bloque quelque part.

### 2. Connexion et gestion des rôles
Quand on arrive sur l'application (sur `Home.py`), on tombe d'abord sur un formulaire de connexion. Dans une vraie usine, tout le monde ne doit pas avoir accès aux mêmes chiffres de production, donc on a mis en place un système de rôles :
*   **L'Administrateur** (`admin@telefan.com`) : Il a accès à tous les onglets. Surtout, c'est le seul qui possède le bouton magique sur l'accueil pour "importer de nouvelles données" et mettre à jour le dashboard avec un nouveau fichier SQL FESTO.
*   **Le Responsable Opérations** (`ops@telefan.com`) : Son but, c'est que la ligne crache des pièces conformes. On lui a donné accès aux pages Performance, Qualité et Maintenance, mais on lui a caché la partie Logistique qui ne le regarde pas forcément.
*   **Le Responsable Supply Chain** (`supply@telefan.com`) : À l'inverse, lui gère les flux et les délais clients. Il a accès à la Logistique et à la Qualité, mais pas à la maintenance pure des machines.

### 3. Les fonctionnalités "Transverses" (Communes à tout le site)
Peu importe la page où on se trouve, on a rajouté des outils bien pratiques :
*   **La barre de filtres (Sidebar)** : Sur la gauche, on peut filtrer les données par plage de dates ou par ressource (machine). C'est super utile si on veut par exemple isoler un problème de cadence qui a eu lieu la semaine dernière uniquement sur le Poste 2.
*   **Le Mode Diaporama** : C'était une fonctionnalité importante pour nous. L'idée c'est qu'on puisse mettre le dashboard sur une grosse télé au-dessus de la ligne de production. On active le mode diapo, et les pages défilent toutes seules (on peut régler la vitesse) sans que personne n'ait besoin de toucher une souris.

### 4. Le cœur du Dashboard : Détail des pages et lien avec les indicateurs
C'est ici qu'on fait le lien direct avec notre analyse des données. Chaque page répond à un besoin spécifique du cahier des charges.

**Page Performance (Bleue) - Axe "Efficacité globale"**
C'est la vue principale pour voir si la ligne produit. 
*   On y a mis en gros le **TRS (Taux de Rendement Synthétique)**. C'est le boss des indicateurs (il combine dispo et qualité). On l'a mis sous forme de jauge avec un objectif visuel à 85% (le standard industriel). 
*   On affiche aussi la **Disponibilité** et la **Cadence** pour comprendre vite fait pourquoi le TRS baisse (est-ce que la machine est arrêtée ? ou est-ce qu'elle tourne juste trop doucement ?).

**Page Qualité (Verte) - Axe "Qualité produit"**
Produire c'est bien, produire des pièces bonnes, c'est mieux.
*   On suit le **Taux de qualité**.
*   Surtout, on a intégré un graphique de **Pareto des rebuts**. Ça répondait exactement à un besoin métier : selon la loi de Pareto, 20% des causes génèrent 80% des défauts. Ce graphique permet au manager de voir direct quel code d'erreur lui coûte le plus cher, pour dire à ses équipes d'agir là-dessus en priorité.

**Page Logistique / Flux (Rouge) - Axe "Flux et délais"**
Ici on regarde comment les pièces circulent.
*   On surveille le **Lead Time** (le temps de traversée d'une commande) et l'**OTD** (pourcentage de commandes livrées à l'heure).
*   On a créé une fonctionnalité visuelle sympa : la **Heatmap du WIP** (Work In Progress). C'est une grille qui montre l'occupation des zones de stockage (buffers) entre les machines. Visuellement, si on voit une grosse tache rouge sur la heatmap, c'est qu'il y a un bouchon sur la ligne.

**Page Maintenance (Orange) - Axe "Fiabilité équipement"**
Pour que les techniciens sachent quand intervenir.
*   On s'est concentrés sur les pannes avec le **MTBF** (Temps moyen entre pannes : est-ce que la machine est fiable ?) et le **MTTR** (Temps moyen de réparation : est-ce qu'on est rapides pour réparer ?).
*   Ça permet de planifier des interventions avant que la machine ne casse vraiment.

**Page Données (Grise)**
La page pour les curieux.
*   On y trouve un grand tableau récapitulatif de tous les KPIs.
*   On a ajouté un bouton d'export CSV pour que l'utilisateur puisse télécharger les chiffres et faire ses propres tableaux Excel s'il en a besoin.

### 5. La fonctionnalité d'Administration (Import de données)
On ne voulait pas d'un dashboard "jetable" qui ne marche qu'avec notre jeu d'essai. Sur la page d'accueil, l'Admin a une interface où il peut glisser-déposer un nouveau fichier `.sql` issu de la ligne FESTO. Quand il clique sur importer, ça déclenche nos scripts Python en arrière-plan, vide les anciennes tables, insère les nouvelles données et recalcule tous les KPIs. En quelques secondes, le dashboard est à jour avec les vraies données de la journée.

### 6. Notre "filet de sécurité" : Le mode démo
Pendant le développement, on s'est dit "que se passe-t-il si la base de données MySQL plante ou met du temps à démarrer ?". Pour éviter que l'application n'affiche une grosse erreur rouge, on a codé un système de données fictives (`demo_data.py`). Si l'appli n'arrive pas à se connecter à la base, elle bascule automatiquement sur ce mode. Ça affiche un petit message "Attention, données de démonstration", mais ça permet de toujours pouvoir présenter l'interface (lors d'une soutenance par exemple).