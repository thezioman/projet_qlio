# T'EleFan — Tableau de bord MES 4.0

Dashboard de supervision de la ligne de production automatisee **FESTO MES 4.0**, developpe dans le cadre de la SAE MES4.0 a l'IUT Lumiere Lyon 2 (BUT Science des Donnees).

---

## 1. Architecture generale

```
FestoMES-YYYY-MM-DD.sql
        |
        v
pipeline_01_ingestion.py   ->  zone_upload_temp  ->  mcd (base historique)
        |
        v
pipeline_02_eclatement_kpis.py  ->  12 bases kpi_*
        |
        v
Application Streamlit (dashboard)
```

**3 composants Docker :**
- `mysql` — MySQL 8.0 (port 3307), heberge toutes les bases
- `phpmyadmin` — interface d'administration (port 8081)
- `app` — Streamlit (port 8501), pipeline ETL au demarrage

---

## 2. Installation et lancement (Windows 10, Docker)

### Prerequis

- **Docker Desktop** installe et en cours d'execution (https://www.docker.com/products/docker-desktop/)
- Le fichier `FestoMES-2025-12-02.sql` doit etre present a la racine du projet

### Etape 1 : ouvrir un terminal

Ouvrir PowerShell ou l'Invite de commandes et se placer a la racine du projet :

```bash
cd chemin\vers\prog_qlio
```

### Etape 2 : lancer l'application

```bash
docker-compose up --build
```

C'est tout. Docker va automatiquement :
1. Telecharger et demarrer **MySQL 8.0** (port 3307)
2. Demarrer **phpMyAdmin** (port 8081)
3. Construire l'image de l'application Python avec toutes les dependances
4. Creer les bases de donnees et les comptes utilisateurs (`init/01_init.sql`, `init/02_mcd_schema.sql`, `init/setup_users.py`)
5. Lancer le pipeline ETL : ingestion du fichier SQL FESTO puis calcul des 12 KPIs
6. Demarrer **Streamlit** (port 8501)

### Etape 3 : acceder a l'application

| Service | URL | Description |
|---|---|---|
| Dashboard T'EleFan | http://localhost:8501 | Application principale |
| phpMyAdmin | http://localhost:8081 | Administration base de donnees (login: root / root) |

### Arreter l'application

```bash
docker-compose down
```

Pour supprimer egalement les donnees MySQL (remise a zero complete) :

```bash
docker-compose down -v
```

### Paquets Python installes dans le conteneur

Les dependances sont installees automatiquement par Docker a partir du fichier `requirements.txt` :

| Paquet | Version minimale | Role |
|---|---|---|
| `streamlit` | 1.32.0 | Framework web (dashboard) |
| `mysql-connector-python` | 8.3.0 | Connexion MySQL |
| `pandas` | 2.0.0 | Manipulation de donnees (DataFrames) |
| `plotly` | 5.18.0 | Graphiques interactifs (jauges, barres, heatmaps) |
| `pydeck` | 0.8.0 | Visualisation geospatiale (dependance Streamlit) |
| `werkzeug` | 3.0.0 | Hashage securise des mots de passe (pbkdf2:sha256) |
| `numpy` | 1.26.0 | Calculs numeriques (dependance pandas/plotly) |
| `streamlit-autorefresh` | 1.0.1 | Rafraichissement automatique pour le mode diaporama |

L'image Docker utilise **Python 3.11** (image `python:3.11-slim`).

### Configuration Docker

L'application est composee de 3 conteneurs definis dans `docker-compose.yml` :

| Conteneur | Image | Port | Role |
|---|---|---|---|
| `python_project_db` | mysql:8.0 | 3307 | Base de donnees MySQL |
| `python_project_pma` | phpmyadmin/phpmyadmin | 8081 | Interface admin SQL |
| `python_project_app` | Build local (Dockerfile) | 8501 | Application Streamlit + pipeline ETL |

Les donnees MySQL sont persistees dans un volume Docker (`db_data`). Un redemarrage de l'application ne perd pas les donnees.

---

## 3. Comptes utilisateurs

| Email | Mot de passe | Role | Acces |
|---|---|---|---|
| admin@telefan.com | `Admin2024!` | Administrateur | Toutes les pages + import SQL |
| ops@telefan.com | `Ops2024!` | Resp. Operations | Performance, Qualite, Maintenance, Donnees |
| supply@telefan.com | `Supply2024!` | Resp. Logistique | Logistique, Qualite, Donnees |

Les mots de passe sont stockes hashes (werkzeug `pbkdf2:sha256`) en base de donnees.

---

## 4. Description des fonctionnalites

### 4.1 Page d'accueil / Connexion

- Formulaire de connexion (email + mot de passe)
- Authentification contre la base MySQL, fallback sur les comptes de demonstration
- Apres connexion : boutons de navigation colores vers chaque page autorisee
- **Mode diaporama** : cycle automatique entre toutes les pages accessibles avec intervalle configurable (5 a 60 secondes)
- **Import SQL** (admin uniquement) : permet de charger un nouveau fichier `.sql` FESTO pour remplacer le jeu de donnees. Le pipeline ETL est relance automatiquement.

### 4.2 Page Performance (bleue)

Accessible aux roles : `admin`, `manager_ops`

**KPIs affiches :**
- TRS moyen (%) — jauge avec seuils vert/orange/rouge et cible a 85%
- Disponibilite moyenne (%)
- Taux de charge moyen (%)
- Cadence moyenne (pieces/heure)

**Graphiques :**
- Jauge TRS avec indicateur delta par rapport a la cible
- Utilisation des ressources (barres horizontales, % par poste)
- Taux de performance / cadence dans le temps (courbe)
- Taux de disponibilite par ressource (barres verticales avec ligne cible 85%)
- Cycle moyen par ressource (barres verticales, en secondes)

### 4.3 Page Qualite (verte)

Accessible aux roles : `admin`, `manager_ops`, `manager_supply`

**KPIs affiches :**
- Taux de qualite moyen (%)
- Total rebuts (pieces)
- MTBF moyen (minutes)
- MTTR moyen (minutes)

**Graphiques :**
- Jauge taux de qualite avec seuils et cible a 85%
- MTBF / MTTR par ressource (barres groupees)
- Repartition des rebuts par type d'erreur (Pareto : barres + courbe cumul %)

### 4.4 Page Logistique / Flux (rouge)

Accessible aux roles : `admin`, `manager_supply`

**KPIs affiches :**
- Lead Time moyen (minutes)
- OTD moyen (%)
- Commandes analysees (nombre)
- Occupation WIP (%)

**Graphiques :**
- Tableau OTD detaille (date, commandes totales, a l'heure, OTD %)
- Heatmap WIP : grille binaire (0 = libre, 1 = occupe) par ligne de production et par date
- Stock par reference (Pareto : barres + courbe cumul %)
- Lead Time moyen par ressource (barres verticales)

### 4.5 Page Maintenance (orange)

Accessible aux roles : `admin`, `manager_ops`

**KPIs affiches :**
- Nombre total d'erreurs
- MTBF moyen (minutes)
- MTTR moyen (minutes)
- Nombre de ressources suivies

**Graphiques :**
- Indicateur grand format du nombre d'erreurs
- Duree moyenne d'indisponibilite par ressource (MTTR, barres horizontales)
- Repartition d'erreurs par ressource (Pareto : barres + courbe cumul %)
- Repartition par type d'erreur (barres verticales)

### 4.6 Page Donnees (grise)

Accessible aux roles : `admin`, `manager_ops`, `manager_supply`

**3 onglets :**

1. **Synthese KPI** : tableau recapitulatif de tous les indicateurs avec valeur, statut (OK/Attention/KO), cible et source de donnees
2. **Donnees brutes** : exploration des tables KPI avec selecteur, filtre par date et par ressource
3. **Export CSV** : telechargement de n'importe quel KPI au format CSV (separateur `;`, encodage UTF-8 BOM)

### 4.7 Fonctionnalites transverses

- **Barre de navigation** : boutons colores en haut de chaque page pour naviguer entre les pages autorisees + bouton deconnexion
- **Sidebar filtres** : filtres date debut/fin et multiselect ressources, communs a toutes les pages
- **Indicateur source** : affiche si les donnees proviennent de la base SQL ou du mode demonstration
- **Mode diaporama** : cycle automatique configurable, arretable depuis la sidebar
- **Controle d'acces** : chaque page verifie le role de l'utilisateur et bloque l'acces si non autorise
- **Mode demonstration** : si la base MySQL n'est pas disponible, des donnees simulees sont generees automatiquement

---

## 5. Pipeline ETL

### pipeline_01_ingestion.py

- Lit le fichier SQL FESTO exporte
- Cree une base temporaire `zone_upload_temp`
- Execute les requetes SQL (INSERT, CREATE TABLE) dans cette zone
- Vide les tables de la base `mcd` (TRUNCATE) puis reimporte les donnees
- Supprime la base temporaire

### pipeline_02_eclatement_kpis.py

Recalcule les 12 KPIs a partir de la base `mcd` :

| Fonction | Base KPI | Table | Calcul |
|---|---|---|---|
| `kpi_dispo` | kpi_disponibilite | Disponibilite_Journaliere | % releves en marche / total releves |
| `kpi_perf` | kpi_performance | Performance_Journaliere | Cadence = pieces / temps de production |
| `kpi_qualite` | kpi_qualite | Qualite_Journaliere | % pieces conformes / total pieces |
| `kpi_trs` | kpi_trs | TRS_Journalier | Disponibilite x Qualite |
| `kpi_rebuts` | kpi_rebuts | Rebuts_Journaliers | Comptage erreurs par type et ressource |
| `kpi_lead_time` | kpi_lead_time | Lead_Time_Journalier | TIMESTAMPDIFF debut/fin commande |
| `kpi_otd` | kpi_otd | OTD_Journalier | % commandes terminees avant echeance |
| `kpi_wip` | kpi_wip | WIP_Journalier | Positions occupees / capacite buffer |
| `kpi_taux_charge` | kpi_taux_charge | Taux_Charge_Journalier | % releves actifs / total |
| `kpi_cycle` | kpi_cycle_moyen | Cycle_Moyen_Journalier | Duree moyenne par operation |
| `kpi_fiabilite` | kpi_fiabilite | Fiabilite_Journaliere | MTBF/MTTR par analyse evenements |
| `kpi_stock` | kpi_stock | Stock_Actuel | Somme quantites par piece |

---

## 6. Importer un nouveau jeu de donnees

**Via l'interface (recommande) :**
Connectez-vous en tant qu'admin -> section "Importer un nouveau jeu de donnees SQL" -> charger le fichier `.sql` -> "Lancer l'import".

**Via le terminal :**
```bash
docker cp FestoMES-YYYY-MM-DD.sql python_project_app:/app/_upload_tmp.sql
docker exec python_project_app python pipeline_01_ingestion.py /app/_upload_tmp.sql
docker exec python_project_app python pipeline_02_eclatement_kpis.py
```

---

## 7. Structure du projet

```
prog_qlio/
|-- Home.py                        # Page d'accueil et connexion
|-- auth.py                        # Authentification, navbar, filtres sidebar
|-- db.py                          # Connexions MySQL, chargement des KPIs
|-- demo_data.py                   # Donnees de demonstration (fallback)
|-- pipeline_01_ingestion.py       # ETL : import SQL -> mcd
|-- pipeline_02_eclatement_kpis.py # ETL : mcd -> 12 bases kpi_*
|-- pages/
|   |-- 1_Performance.py
|   |-- 2_Qualite.py
|   |-- 3_Logistique.py
|   |-- 4_Maintenance.py
|   +-- 5_Donnees.py
|-- init/
|   |-- 01_init.sql                # Creation base python_auth_db + table users
|   |-- 02_mcd_schema.sql          # Schema base historique mcd
|   +-- setup_users.py             # Insertion des comptes au demarrage
|-- .streamlit/
|   +-- config.toml                # Theme Streamlit (light)
|-- schema_mcd_v2.sql              # Schema MCD complet
|-- docker-compose.yml
|-- Dockerfile
|-- entrypoint.sh
+-- requirements.txt
```

---

## 8. Bases de donnees

| Base | Contenu |
|---|---|
| `python_auth_db` | Comptes utilisateurs (email, hash mot de passe, role) |
| `mcd` | Donnees historiques consolidees (Commande, Ressource, Execution, Surveillance...) |
| `zone_upload_temp` | Zone tampon pour l'import SQL brut (supprimee apres transfert) |
| `kpi_trs` | TRS journalier par ressource |
| `kpi_disponibilite` | Disponibilite journaliere par ressource |
| `kpi_performance` | Cadence journaliere par ressource |
| `kpi_qualite` | Taux de qualite journalier par ressource |
| `kpi_rebuts` | Rebuts journaliers par type d'erreur |
| `kpi_fiabilite` | MTBF / MTTR journalier par ressource |
| `kpi_lead_time` | Lead time par commande |
| `kpi_otd` | On-Time Delivery journalier |
| `kpi_wip` | Taux d'occupation WIP par ressource |
| `kpi_taux_charge` | Taux de charge journalier par ressource |
| `kpi_cycle_moyen` | Cycle moyen journalier par ressource |
| `kpi_stock` | Stock actuel par piece |

---

IUT Lumiere Lyon 2 — BUT Science des Donnees — SAE MES 4.0
