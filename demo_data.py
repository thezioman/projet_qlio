"""Génération de données de démonstration pour tous les KPIs."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

POSTES = [f"Poste {i}" for i in range(1, 11)]
POSTES_IDS = list(range(1, 11))
ERRORS = [
    "Défaut assemblage",
    "Mauvais positionnement",
    "Circuit non conforme",
    "Fusible manquant",
    "Coque abîmée",
]
PIECES = ["Coque inf.", "Circuit imprimé", "Fusible", "Coque sup."]
N_DAYS = 30


def _dates(n=N_DAYS):
    end = datetime.now().date()
    return [end - timedelta(days=i) for i in range(n - 1, -1, -1)]


def _rng(seed=42):
    """Retourne un générateur fixe — mêmes valeurs à chaque appel."""
    return np.random.default_rng(seed=seed)


# ---------- KPI Performance ----------
def get_trs_demo(start=None, end=None):
    rng = _rng()
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            trs = float(rng.uniform(68, 94))
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname, "TRS_Pourcent": round(trs, 1)})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_dispo_demo(start=None, end=None):
    rng = _rng(1)
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            dispo = float(rng.uniform(78, 99))
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                         "Disponibilite_Pourcent": round(dispo, 1)})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_perf_demo(start=None, end=None):
    rng = _rng(2)
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            pieces = int(rng.integers(80, 200))
            cadence = round(float(rng.uniform(50, 120)), 1)
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                         "Pieces_Produites": pieces, "Cadence_Pieces_Par_Heure": cadence})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_cycle_demo(start=None, end=None):
    rng = _rng(3)
    rows = []
    ops = ["Assemblage", "Pressage", "Contrôle vision", "Pick-by-Light", "Palettisation"]
    base_times = [12.5, 18.3, 8.7, 22.1, 15.4, 30.0, 11.2, 19.8, 14.6, 25.3]
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            op = ops[pid % len(ops)]
            cycle = round(base_times[pid - 1] + float(rng.uniform(-2, 4)), 1)
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                         "Description_Operation": op, "Cycle_Moyen_Secondes": cycle})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_charge_demo(start=None, end=None):
    rng = _rng(4)
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            charge = float(rng.uniform(60, 95))
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                         "Taux_Charge_Pourcent": round(charge, 1)})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


# ---------- KPI Qualité ----------
def get_qualite_demo(start=None, end=None):
    rng = _rng(5)
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            taux = float(rng.uniform(82, 99))
            total = int(rng.integers(100, 200))
            conformes = int(total * taux / 100)
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                         "Total_Pieces": total, "Pieces_Conformes": conformes,
                         "Taux_Qualite_Pourcent": round(taux, 1)})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_rebuts_demo(start=None, end=None, postes=None):
    rng = _rng(6)
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            if postes and pname not in postes:
                continue
            for err in ERRORS:
                nb = int(rng.integers(0, 15))
                if nb > 0:
                    rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                                 "Description_Erreur": err, "Nb_Rebuts": nb})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_fiabilite_demo(start=None, end=None):
    rng = _rng(7)
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            mtbf = round(float(rng.uniform(120, 480)), 1)
            mttr = round(float(rng.uniform(5, 45)), 1)
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                         "MTBF_Minutes": mtbf, "MTTR_Minutes": mttr})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


# ---------- KPI Logistique ----------
def get_lead_time_demo(start=None, end=None):
    rng = _rng(8)
    rows = []
    for d in _dates():
        for cmd_id in range(1, 11):
            lt = int(rng.integers(15, 120))
            rows.append({"Date_Jour": d, "ID_Commande": cmd_id, "Lead_Time_Minutes": lt})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_otd_demo(start=None, end=None):
    rng = _rng(9)
    rows = []
    for d in _dates():
        total = int(rng.integers(5, 20))
        a_heure = int(rng.integers(int(total * 0.6), total + 1))
        otd = round(a_heure / total * 100, 1)
        rows.append({"Date_Jour": d, "Total_Commandes": total,
                     "Commandes_A_L_Heure": a_heure, "OTD_Pourcent": otd})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_wip_demo(start=None, end=None):
    rng = _rng(10)
    rows = []
    for d in _dates():
        for pid, pname in zip(POSTES_IDS, POSTES):
            capa = 20
            occ = round(float(rng.uniform(4, 18)), 1)
            taux = round(occ / capa * 100, 1)
            rows.append({"Date_Jour": d, "ID_Ressource": pid, "Poste": pname,
                         "Moyenne_Positions_Occupees": occ,
                         "Capacite_Totale": capa, "Taux_Occupation_Pourcent": taux})
    df = pd.DataFrame(rows)
    if start:
        df = df[df["Date_Jour"] >= start]
    if end:
        df = df[df["Date_Jour"] <= end]
    return df


def get_stock_demo():
    rng = _rng(11)
    rows = []
    for piece in PIECES:
        qty = int(rng.integers(20, 200))
        rows.append({"Description_Piece": piece, "Quantite_Totale": qty})
    return pd.DataFrame(rows)
