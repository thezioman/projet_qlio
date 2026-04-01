# T'EleFan — Tableau de bord MES 4.0

Dashboard de supervision de la ligne de production automatisée **FESTO MES 4.0**, développé dans le cadre de la SAE MES4.0 à l'IUT Lumière Lyon 2 (BUT Science des Données).

---

## Architecture générale

```
FestoMES-YYYY-MM-DD.sql
        │
        ▼
pipeline_01_ingestion.py   →  zone_upload_temp  →  mcd (base historique)
        │
        ▼
pipeline_02_eclatement_kpis.py  →  12 bases kpi_*
        │
        ▼
Application Streamlit (dashboard)
```

**3 composants Docker :**
- `mysql` — MySQL 8.0 (port 3307), héberge toutes les bases
- `phpmyadmin` — interface d'administration (port 8081)
- `app` — Streamlit (port 8501), pipeline ETL au démarrage

---

## Lancement

### Prérequis
- Docker Desktop installé et en cours d'exécution

### Démarrage
```bash
docker-compose up --build
```

L'application est disponible sur [http://localhost:8501](http://localhost:8501).
phpMyAdmin est disponible sur [http://localhost:8081](http://localhost:8081).

Au premier démarrage, le pipeline ETL est lancé automatiquement :
1. Ingestion de `FestoMES-2025-12-02.sql` dans la base temporaire
2. Transfert vers la base historique `mcd` (anti-doublons)
3. Calcul des 12 KPIs journaliers par ressource
4. Création des comptes utilisateurs

---

## Comptes utilisateurs

| Email | Mot de passe | Rôle | Accès |
|---|---|---|---|
| admin@telefan.com | `Admin2024!` | Administrateur | Toutes les pages + import SQL |
| ops@telefan.com | `Ops2024!` | Resp. Opérations | Performance, Qualité, Données |
| supply@telefan.com | `Supply2024!` | Resp. Logistique | Logistique, Qualité, Données |

Les mots de passe sont stockés hashés (werkzeug `pbkdf2:sha256`) en base de données.

---

## Pages du dashboard

| Page | Couleur | Indicateurs |
|---|---|---|
| Performance | Bleu | TRS, Disponibilité, Cadence, Cycle moyen, Taux de charge |
| Qualité | Vert | Taux de qualité, Rebuts (Pareto), MTBF/MTTR |
| Logistique / Flux | Rouge | Lead Time, OTD, WIP (heatmap), Stock (Pareto) |
| Données | Gris | Tableaux bruts, synthèse KPI, export CSV |

Fonctionnalités transverses :
- Filtres date et ressource dans la sidebar
- Mode diaporama (cycle automatique entre les pages)
- Import d'un nouveau fichier SQL depuis l'accueil (admin uniquement)

---

## Importer un nouveau jeu de données

Deux méthodes :

**Via l'interface (recommandé) :**
Connectez-vous en tant qu'admin → section "Importer un nouveau jeu de données SQL" → charger le fichier `.sql` → "Lancer l'import".

**Via le terminal :**
```bash
# Copier le fichier dans le container
docker cp FestoMES-YYYY-MM-DD.sql python_project_app:/app/_upload_tmp.sql

# Lancer le pipeline
docker exec python_project_app python pipeline_01_ingestion.py /app/_upload_tmp.sql
docker exec python_project_app python pipeline_02_eclatement_kpis.py
```

---

## Structure du projet

```
├── Home.py                        # Page d'accueil et connexion
├── auth.py                        # Authentification, navbar, filtres sidebar
├── db.py                          # Connexions MySQL, chargement des KPIs
├── demo_data.py                   # Données de démonstration (fallback)
├── pipeline_01_ingestion.py       # ETL : import SQL → mcd
├── pipeline_02_eclatement_kpis.py # ETL : mcd → 12 bases kpi_*
├── pages/
│   ├── 1_Performance.py
│   ├── 2_Qualite.py
│   ├── 3_Logistique.py
│   └── 5_Donnees.py
├── init/
│   ├── 01_init.sql                # Création base python_auth_db + table users
│   ├── 02_mcd_schema.sql          # Schéma base historique mcd
│   └── setup_users.py             # Insertion des comptes au démarrage
├── schema_mcd_v2.sql              # Schéma MCD complet
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
└── requirements.txt
```

---

## Bases de données

| Base | Contenu |
|---|---|
| `python_auth_db` | Comptes utilisateurs (email, hash mot de passe, rôle) |
| `mcd` | Données historiques consolidées (Commande, Ressource, Execution, Surveillance...) |
| `zone_upload_temp` | Zone tampon pour l'import SQL brut |
| `kpi_trs` | TRS journalier par ressource |
| `kpi_disponibilite` | Disponibilité journalière par ressource |
| `kpi_performance` | Cadence journalière par ressource |
| `kpi_qualite` | Taux de qualité journalier par ressource |
| `kpi_rebuts` | Rebuts journaliers par type d'erreur |
| `kpi_fiabilite` | MTBF / MTTR journalier par ressource |
| `kpi_lead_time` | Lead time par commande |
| `kpi_otd` | On-Time Delivery journalier |
| `kpi_wip` | Taux d'occupation WIP par ressource |
| `kpi_taux_charge` | Taux de charge journalier par ressource |
| `kpi_cycle_moyen` | Cycle moyen journalier par ressource |
| `kpi_stock` | Stock actuel par pièce |

---

IUT Lumière Lyon 2 — BUT Science des Données — SAE MES 4.0
