# Documentation technique de l'environnement de travail – Projet T'EleFan

### 1. Introduction
Ce document présente l'environnement technique qu'on a mis en place pour la création de notre dashboard

Dès le départ, on s'est posé la question de l'environnement de développement. Pour éviter les problèmes d'installation entre les différents PC du groupe, on a décidé de tout gérer avec Docker. Ça permet d'avoir un environnement isolé et prêt à l'emploi.

### 2. L'architecture globale avec Docker
Toute notre infrastructure tourne grâce au fichier `docker-compose.yml`. On a découpé le projet en trois conteneurs qui communiquent entre eux :

*   **Le conteneur base de données (`python_project_db`)** : C'est un serveur MySQL 8.0 qui tourne sur le port 3307. Il stocke la base principale `mcd` et toutes les bases `kpi_*` qu'on génère pour le dashboard.
*   **Le conteneur PhpMyAdmin (`python_project_pma`)** : Accessible sur le port 8081. On l'a ajouté surtout pour nous faciliter la vie pendant le développement, pour pouvoir aller vérifier visuellement si nos scripts Python remplissaient bien les tables SQL correctement.
*   **Le conteneur de l'application (`python_project_app`)** : C'est là que tourne notre code Python. Il gère à la fois les scripts de traitement de données (notre pipeline ETL) et l'affichage du dashboard Streamlit sur le port 8501.

### 3. Le Backend : Base de données et persistance
Pour la base de données, on est partis sur MySQL parce que c'est ce qu'on maîtrise le mieux et que ça correspondait bien à la structure des données FESTO. 

Un point important qu'on a dû gérer, c'est la perte des données. Par défaut, quand on coupe un conteneur Docker, il supprime tout. On a donc configuré un volume Docker (nommé `db_data`) pour sauvegarder les données SQL. Comme ça, si on redémarre le projet on ne perd pas la base.

Pour l'initialisation, on a placé des scripts dans le dossier `init/`. Au tout premier lancement, MySQL va lire ces fichiers pour créer automatiquement la structure de la base (les tables du MCD) et ajouter les comptes utilisateurs par défaut avec leurs mots de passe hashés.

### 4. Le Frontend et les traitements Python
Côté code, on utilise `python:3.11-slim`. Toutes nos bibliothèques sont listées dans le `requirements.txt`. On y retrouve :
*   `streamlit` pour faire l'interface web
*   `pandas` et `numpy` pour manipuler les données
*   `plotly` pour tracer les graphiques et les jauges
*   `mysql-connector-python` pour lier Python et la base de données

La particularité de notre conteneur app, c'est son script de démarrage (`entrypoint.sh`). Avant de lancer l'interface Streamlit, il exécute automatiquement nos deux scripts Python de traitement de données (`pipeline_01_ingestion.py` et `pipeline_02_eclatement_kpis.py`). Ça garantit que quand l'utilisateur arrive sur la page web, les indicateurs sont déjà calculés et prêts à être affichés.

### 5. Guide d'utilisation (Comment lancer le projet)
C'est la partie la plus simple puisqu'on a tout automatisé.

**Prérequis :**
Il faut juste avoir Docker Desktop d'installé et lancé sur la machine.

**Pour lancer l'application :**
Ouvrir un terminal à la racine du projet et taper :
```bash
docker-compose up --build
```
La première fois, ça prend un peu de temps parce que Docker télécharge les images (MySQL, Python) et installe les bibliothèques du `requirements.txt`. Ensuite, il démarre les bases de données, lance les calculs Python, et ouvre le serveur web.

**Pour y accéder :**
*   Le dashboard T'EleFan : `http://localhost:8501`
*   L'interface PhpMyAdmin : `http://localhost:8081` (identifiant: root / mot de passe: root)

**Pour arrêter le projet :**
dans le terminal, taper la commande :
```bash
docker-compose down
```
Si on veut faire un nettoyage complet et remettre la base de données à zéro (par exemple pour tester une installation toute propre), il faut rajouter l'option `-v` pour supprimer les volumes : `docker-compose down -v`.

### 6. S'y retrouver dans les dossiers
Pour comprendre comment le code est rangé, voici l'organisation principale :

*   `Home.py` : Le point d'entrée du dashboard (page de connexion).
*   `pages/` : Ce dossier contient les fichiers de chaque onglet du site (1_Performance.py, 2_Qualite.py, etc.). Streamlit crée le menu automatiquement à partir de ce dossier.
*   `auth.py` et `db.py` : Nos fichiers utilitaires. Le premier gère qui a le droit de voir quoi, le deuxième s'occupe de faire les requêtes SQL.
*   `pipeline_*.py` : Nos scripts qui ingèrent le fichier SQL de FESTO et qui calculent les KPIs.
*   `init/` : Les fameux scripts SQL et Python qui préparent la base au tout premier lancement de Docker.

IUT Lumiere Lyon 2 — BUT Science des Donnees — SAE MES 4.0