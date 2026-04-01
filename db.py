"""Helpers de connexion à MySQL pour les bases KPI et auth."""
import os
import mysql.connector
import pandas as pd
from datetime import date, timedelta

_MYSQL_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", "3307")),
    "user":     os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "root"),
}


def _conn(database=None):
    cfg = dict(_MYSQL_CONFIG)
    if database:
        cfg["database"] = database
    return mysql.connector.connect(**cfg)


def db_available(kpi_db: str) -> bool:
    try:
        conn = _conn(kpi_db)
        conn.close()
        return True
    except Exception:
        return False


def get_kpi_df(kpi_db: str, table: str,
               date_col="Date_Jour",
               start_date=None, end_date=None) -> pd.DataFrame | None:
    """
    Lit une table KPI avec filtre de date strict.
    Retourne None si la base/table n'existe pas ou si aucune donnée ne correspond.
    """
    try:
        conn = _conn(kpi_db)
        if date_col and start_date and end_date:
            where = f"WHERE {date_col} >= '{start_date}' AND {date_col} <= '{end_date}'"
        else:
            where = ""
        df = pd.read_sql(f"SELECT * FROM {table} {where}", conn)
        conn.close()
        return df if not df.empty else None
    except Exception:
        return None


def get_date_range() -> tuple[date, date]:
    """
    Détecte la plage de dates réelle dans les données KPI.
    Retourne (min_date, max_date).
    """
    for kpi_db, table, col in [
        ("kpi_disponibilite", "Disponibilite_Journaliere", "Date_Jour"),
        ("kpi_trs",           "TRS_Journalier",            "Date_Jour"),
        ("kpi_qualite",       "Qualite_Journaliere",       "Date_Jour"),
    ]:
        try:
            conn = _conn(kpi_db)
            cur = conn.cursor()
            cur.execute(f"SELECT MIN({col}), MAX({col}) FROM {table}")
            row = cur.fetchone()
            conn.close()
            if row and row[0] and row[1]:
                return row[0], row[1]
        except Exception:
            continue
    today = date.today()
    return today - timedelta(days=30), today


def get_resources() -> dict:
    """Retourne {ID_RESSOURCE: NOM_RESSOURCE} depuis la base mcd."""
    try:
        conn = _conn("mcd")
        df = pd.read_sql("SELECT ID_RESSOURCE, NOM_RESSOURCE FROM Ressource WHERE ID_RESSOURCE > 0", conn)
        conn.close()
        return dict(zip(df["ID_RESSOURCE"], df["NOM_RESSOURCE"]))
    except Exception:
        return {i: f"Poste {i}" for i in range(1, 11)}
