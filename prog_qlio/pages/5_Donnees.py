import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import check_auth, render_navbar, render_sidebar_filters, handle_slideshow
from db import get_kpi_df, db_available
import demo_data as demo

st.set_page_config(layout="wide", page_title="Donnees – T'EleFan",
                   initial_sidebar_state="expanded")

check_auth(allowed_roles=["admin", "manager_ops", "manager_supply"])

handle_slideshow("Donnees", st.session_state.get("slideshow_interval", 15))

st.markdown("""
<style>
.stApp {background-color: #F5F5F5;}
.stApp, .stApp p, .stApp span, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stMarkdown, .stMarkdown p {color: #1a1a1a !important;}

/* Onglets : texte foncé sur fond clair */
[data-baseweb="tab"] p,
[data-baseweb="tab"] span,
button[role="tab"] p,
button[role="tab"] span {color: #1a1a1a !important;}

.header-page {
    background: #555555; color: white; padding: 12px 20px;
    border-radius: 8px; font-family: Arial; font-size: 20px;
    font-weight: bold; margin-bottom: 18px;
}
.kpi-box {
    background: white; border-left: 5px solid #404040;
    padding: 12px 16px; border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 10px;
}
.kpi-label {font-size: 11px; color: #777; font-family: Arial;}
.kpi-value {font-size: 13px; font-weight: bold; font-family: Arial;}
</style>
""", unsafe_allow_html=True)

render_navbar(active="Donnees")

# render_sidebar_filters retourne (start_date, end_date, resource_ids) — resource_ids est une liste d'int
start_date, end_date, resource_ids = render_sidebar_filters()

st.markdown("<div class='header-page'>Acces aux Donnees — T'EleFan</div>",
            unsafe_allow_html=True)

KPI_TABLES = [
    ("kpi_trs",           "TRS_Journalier",            "TRS"),
    ("kpi_disponibilite", "Disponibilite_Journaliere", "Disponibilite"),
    ("kpi_performance",   "Performance_Journaliere",   "Performance"),
    ("kpi_qualite",       "Qualite_Journaliere",       "Qualite"),
    ("kpi_rebuts",        "Rebuts_Journaliers",        "Rebuts"),
    ("kpi_lead_time",     "Lead_Time_Journalier",      "Lead Time"),
    ("kpi_otd",           "OTD_Journalier",            "OTD"),
    ("kpi_wip",           "WIP_Journalier",            "WIP"),
    ("kpi_taux_charge",   "Taux_Charge_Journalier",    "Taux de charge"),
    ("kpi_cycle_moyen",   "Cycle_Moyen_Journalier",    "Cycle moyen"),
    ("kpi_fiabilite",     "Fiabilite_Journaliere",     "Fiabilite MTBF/MTTR"),
    ("kpi_stock",         "Stock_Actuel",              "Stock"),
]

# Etat des sources
st.markdown("### Etat des sources de donnees")
cols = st.columns(4)
for i, (db_name, table, label) in enumerate(KPI_TABLES):
    avail = db_available(db_name)
    with cols[i % 4]:
        status_color = "#5E8E47" if avail else "#E67E22"
        status_text  = "BD en ligne" if avail else "Demo"
        st.markdown(
            f'<div class="kpi-box">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{status_color}">● {status_text}</div>'
            f'<div class="kpi-label" style="margin-top:2px">{db_name}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

tab_kpi, tab_brut, tab_export = st.tabs(["Synthese KPI", "Donnees brutes", "Export CSV"])

# ─── TAB 1 : Synthese ───────────────────────────────────────────────────────
with tab_kpi:
    st.markdown("**Synthese de tous les indicateurs — periode selectionnee**")

    def _load(db_name, table, date_col="Date_Jour"):
        if db_available(db_name):
            df = get_kpi_df(db_name, table, date_col=date_col,
                            start_date=start_date if date_col else None,
                            end_date=end_date if date_col else None)
            if df is not None and not df.empty:
                return df, True
        return None, False

    def _filter(df):
        if df is not None and resource_ids and "ID_Ressource" in df.columns:
            return df[df["ID_Ressource"].isin(resource_ids)]
        return df

    rows = []

    df, live = _load("kpi_trs", "TRS_Journalier")
    if df is None: df = demo.get_trs_demo(start_date, end_date)
    df = _filter(df)
    val = df["TRS_Pourcent"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "TRS", "Valeur": f"{val:.1f} %" if val is not None else "—",
                 "Statut": ("OK" if val and val>=85 else "Att." if val and val>=70 else "KO"),
                 "Cible": ">= 85 %", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_disponibilite", "Disponibilite_Journaliere")
    if df is None: df = demo.get_dispo_demo(start_date, end_date)
    df = _filter(df)
    val = df["Disponibilite_Pourcent"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "Disponibilite", "Valeur": f"{val:.1f} %" if val is not None else "—",
                 "Statut": ("OK" if val and val>=85 else "Att." if val and val>=70 else "KO"),
                 "Cible": ">= 85 %", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_performance", "Performance_Journaliere")
    if df is None: df = demo.get_perf_demo(start_date, end_date)
    df = _filter(df)
    val = df["Cadence_Pieces_Par_Heure"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "Cadence", "Valeur": f"{val:.1f} pcs/h" if val is not None else "—",
                 "Statut": "Info", "Cible": "—", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_qualite", "Qualite_Journaliere")
    if df is None: df = demo.get_qualite_demo(start_date, end_date)
    df = _filter(df)
    val = df["Taux_Qualite_Pourcent"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "Qualite", "Valeur": f"{val:.1f} %" if val is not None else "—",
                 "Statut": ("OK" if val and val>=85 else "Att." if val and val>=75 else "KO"),
                 "Cible": ">= 85 %", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_rebuts", "Rebuts_Journaliers")
    if df is None: df = demo.get_rebuts_demo(start_date, end_date)
    df = _filter(df)
    val = int(df["Nb_Rebuts"].sum()) if df is not None and not df.empty else None
    rows.append({"KPI": "Rebuts total", "Valeur": f"{val} pcs" if val is not None else "—",
                 "Statut": ("OK" if val is not None and val<50 else "Att." if val is not None and val<100 else "KO"),
                 "Cible": "< 50 pcs", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_lead_time", "Lead_Time_Journalier")
    if df is None: df = demo.get_lead_time_demo(start_date, end_date)
    val = df["Lead_Time_Minutes"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "Lead Time moyen", "Valeur": f"{val:.0f} min" if val is not None else "—",
                 "Statut": "Info", "Cible": "—", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_otd", "OTD_Journalier")
    if df is None: df = demo.get_otd_demo(start_date, end_date)
    val = df["OTD_Pourcent"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "OTD", "Valeur": f"{val:.1f} %" if val is not None else "—",
                 "Statut": ("OK" if val and val>=90 else "Att." if val and val>=70 else "KO"),
                 "Cible": ">= 90 %", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_wip", "WIP_Journalier")
    if df is None: df = demo.get_wip_demo(start_date, end_date)
    val = df["Taux_Occupation_Pourcent"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "WIP occupation", "Valeur": f"{val:.1f} %" if val is not None else "—",
                 "Statut": ("OK" if val is not None and val<=80 else "Att." if val is not None and val<=90 else "KO"),
                 "Cible": "<= 80 %", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_taux_charge", "Taux_Charge_Journalier")
    if df is None: df = demo.get_charge_demo(start_date, end_date)
    df = _filter(df)
    val = df["Taux_Charge_Pourcent"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "Taux de charge", "Valeur": f"{val:.1f} %" if val is not None else "—",
                 "Statut": ("OK" if val and val>=70 else "Att." if val and val>=50 else "KO"),
                 "Cible": ">= 80 %", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_cycle_moyen", "Cycle_Moyen_Journalier")
    if df is None: df = demo.get_cycle_demo(start_date, end_date)
    df = _filter(df)
    val = df["Cycle_Moyen_Secondes"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "Cycle moyen", "Valeur": f"{val:.1f} s" if val is not None else "—",
                 "Statut": "Info", "Cible": "—", "Source": "BD" if live else "Demo"})

    df, live = _load("kpi_fiabilite", "Fiabilite_Journaliere")
    if df is None: df = demo.get_fiabilite_demo(start_date, end_date)
    df = _filter(df)
    mtbf = df["MTBF_Minutes"].mean() if df is not None and not df.empty else None
    mttr = df["MTTR_Minutes"].mean() if df is not None and not df.empty else None
    rows.append({"KPI": "MTBF", "Valeur": f"{min(mtbf, 9999):.0f} min" if mtbf else "—",
                 "Statut": ("OK" if mtbf and mtbf>=120 else "Att." if mtbf and mtbf>=60 else "KO"),
                 "Cible": ">= 120 min", "Source": "BD" if live else "Demo"})
    rows.append({"KPI": "MTTR", "Valeur": f"{mttr:.0f} min" if mttr else "—",
                 "Statut": ("OK" if mttr and mttr<=30 else "Att." if mttr and mttr<=60 else "KO"),
                 "Cible": "<= 30 min", "Source": "BD" if live else "Demo"})

    df_s, live_s = _load("kpi_stock", "Stock_Actuel", date_col=None)
    if df_s is None: df_s = demo.get_stock_demo()
    val_s = int(df_s["Quantite_Totale"].sum()) if df_s is not None and not df_s.empty else None
    rows.append({"KPI": "Stock total", "Valeur": f"{val_s} pcs" if val_s is not None else "—",
                 "Statut": "Info", "Cible": "—", "Source": "BD" if live_s else "Demo"})

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=500)

# ─── TAB 2 : Donnees brutes ──────────────────────────────────────────────────
with tab_brut:
    selected_kpi = st.selectbox("KPI :", options=[lbl for _, _, lbl in KPI_TABLES])
    idx = [lbl for _, _, lbl in KPI_TABLES].index(selected_kpi)
    db_name, table, _ = KPI_TABLES[idx]
    date_col = None if db_name == "kpi_stock" else "Date_Jour"

    df_raw = None
    src = "Demo"
    if db_available(db_name):
        df_raw = get_kpi_df(db_name, table, date_col=date_col,
                            start_date=start_date if date_col else None,
                            end_date=end_date if date_col else None)
        if df_raw is not None and not df_raw.empty:
            src = "Base de donnees"

    if df_raw is None or df_raw.empty:
        fallback = {
            "kpi_trs":           lambda: demo.get_trs_demo(start_date, end_date),
            "kpi_disponibilite": lambda: demo.get_dispo_demo(start_date, end_date),
            "kpi_performance":   lambda: demo.get_perf_demo(start_date, end_date),
            "kpi_qualite":       lambda: demo.get_qualite_demo(start_date, end_date),
            "kpi_rebuts":        lambda: demo.get_rebuts_demo(start_date, end_date),
            "kpi_lead_time":     lambda: demo.get_lead_time_demo(start_date, end_date),
            "kpi_otd":           lambda: demo.get_otd_demo(start_date, end_date),
            "kpi_wip":           lambda: demo.get_wip_demo(start_date, end_date),
            "kpi_taux_charge":   lambda: demo.get_charge_demo(start_date, end_date),
            "kpi_cycle_moyen":   lambda: demo.get_cycle_demo(start_date, end_date),
            "kpi_fiabilite":     lambda: demo.get_fiabilite_demo(start_date, end_date),
            "kpi_stock":         lambda: demo.get_stock_demo(),
        }
        df_raw = fallback[db_name]()

    if resource_ids and df_raw is not None and "ID_Ressource" in df_raw.columns:
        df_raw = df_raw[df_raw["ID_Ressource"].isin(resource_ids)]

    st.caption(f"Source : {src} — {len(df_raw):,} lignes")
    st.dataframe(df_raw, use_container_width=True, height=480)

# ─── TAB 3 : Export CSV ──────────────────────────────────────────────────────
with tab_export:
    col_l, col_r = st.columns([1, 2])

    with col_l:
        export_kpi = st.selectbox("KPI a exporter :", options=[lbl for _, _, lbl in KPI_TABLES],
                                  key="export_select")
        exp_idx = [lbl for _, _, lbl in KPI_TABLES].index(export_kpi)
        exp_db, exp_table, exp_label = KPI_TABLES[exp_idx]
        filter_resources = st.checkbox("Filtrer par ressources selectionnees", value=False)

    with col_r:
        date_col_e = None if exp_db == "kpi_stock" else "Date_Jour"
        df_exp = None

        if db_available(exp_db):
            df_exp = get_kpi_df(exp_db, exp_table, date_col=date_col_e,
                                start_date=start_date if date_col_e else None,
                                end_date=end_date if date_col_e else None)

        if df_exp is None or df_exp.empty:
            fallback_e = {
                "kpi_trs":           lambda: demo.get_trs_demo(start_date, end_date),
                "kpi_disponibilite": lambda: demo.get_dispo_demo(start_date, end_date),
                "kpi_performance":   lambda: demo.get_perf_demo(start_date, end_date),
                "kpi_qualite":       lambda: demo.get_qualite_demo(start_date, end_date),
                "kpi_rebuts":        lambda: demo.get_rebuts_demo(start_date, end_date),
                "kpi_lead_time":     lambda: demo.get_lead_time_demo(start_date, end_date),
                "kpi_otd":           lambda: demo.get_otd_demo(start_date, end_date),
                "kpi_wip":           lambda: demo.get_wip_demo(start_date, end_date),
                "kpi_taux_charge":   lambda: demo.get_charge_demo(start_date, end_date),
                "kpi_cycle_moyen":   lambda: demo.get_cycle_demo(start_date, end_date),
                "kpi_fiabilite":     lambda: demo.get_fiabilite_demo(start_date, end_date),
                "kpi_stock":         lambda: demo.get_stock_demo(),
            }
            df_exp = fallback_e[exp_db]()

        if filter_resources and resource_ids and "ID_Ressource" in df_exp.columns:
            df_exp = df_exp[df_exp["ID_Ressource"].isin(resource_ids)]

        if df_exp is not None and not df_exp.empty:
            st.markdown(f"**Apercu — {exp_label}** ({len(df_exp):,} lignes)")
            st.dataframe(df_exp.head(20), use_container_width=True, height=300)
            csv_data = df_exp.to_csv(index=False, sep=";", encoding="utf-8-sig")
            fname = f"telefan_{exp_db}_{start_date}_{end_date}.csv"
            st.download_button(label=f"Telecharger {exp_label}.csv",
                               data=csv_data, file_name=fname, mime="text/csv")
        else:
            st.info("Aucune donnee disponible pour l'export.")

st.caption("T'EleFan MES 4.0 — Ligne FESTO — IUT Lumiere Lyon 2")
