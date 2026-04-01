#!/bin/bash
set -e

echo "=== Initialisation des utilisateurs ==="
python init/setup_users.py

echo "=== Ingestion des données FESTO ==="
SQL_FILE="/app/FestoMES-2025-12-02.sql"
if [ -f "$SQL_FILE" ]; then
    python pipeline_01_ingestion.py "$SQL_FILE"
    echo "=== Calcul des KPIs ==="
    python pipeline_02_eclatement_kpis.py
else
    echo "Fichier SQL FESTO non trouvé — le dashboard utilisera les données de démonstration."
fi

echo "=== Démarrage de l'application Streamlit ==="
exec streamlit run Home.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
