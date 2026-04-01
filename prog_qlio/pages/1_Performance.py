import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import check_auth, render_navbar, render_sidebar_filters, handle_slideshow
from db import get_kpi_df, db_available
import demo_data as demo

st.set_page_config(layout="wide", page_title="Performance – T'EleFan",
                   initial_sidebar_state="expanded")

check_auth(allowed_roles=["admin", "manager_ops"])

handle_slideshow("Performance", st.session_state.get("slideshow_interval", 15))

st.markdown("""
<style>
.stApp {background-color: #EEF4FB;}
.header-page {
    background: #3d85c8; color: white; padding: 12px 20px;
    border-radius: 8px; font-family: Arial; font-size: 20px;
    font-weight: bold; margin-bottom: 18px;
}
.kpi-box {
    background: #3d85c8; color: white; padding: 14px 18px;
    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); margin-bottom: 12px;
}
.kpi-label {font-size: 12px; color: rgba(255,255,255,0.8); font-family: Arial;}
.kpi-value {font-size: 26px; font-weight: bold; color: white; font-family: Arial;}
.section-title {
    color: white; background: rgba(61,133,200,0.85); padding: 6px 12px;
    border-radius: 6px; font-family: Arial; font-size: 13px;
    font-weight: bold; margin-bottom: 4px; text-align: center;
}
</style>
""", unsafe_allow_html=True)

render_navbar(active="Performance")

start_date, end_date, resource_ids = render_sidebar_filters()

_BG   = "#3d85c8"
_CARD = "rgba(255,255,255,0.12)"
_BAR  = "#E8913D"
_FONT = dict(color="white", family="Arial")
_H    = 340


def _add_poste(df):
    if "ID_Ressource" in df.columns and "Poste" not in df.columns:
        df = df.copy()
        df["Poste"] = df["ID_Ressource"].apply(lambda x: f"Poste {x}")
    return df


def _filter_r(df):
    if "ID_Ressource" in df.columns and resource_ids:
        return df[df["ID_Ressource"].isin(resource_ids)]
    return df


def load_trs():
    if db_available("kpi_trs"):
        df = get_kpi_df("kpi_trs", "TRS_Journalier", start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_trs_demo(start_date, end_date)))


def load_dispo():
    if db_available("kpi_disponibilite"):
        df = get_kpi_df("kpi_disponibilite", "Disponibilite_Journaliere",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_dispo_demo(start_date, end_date)))


def load_perf():
    if db_available("kpi_performance"):
        df = get_kpi_df("kpi_performance", "Performance_Journaliere",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_perf_demo(start_date, end_date)))


def load_cycle():
    if db_available("kpi_cycle_moyen"):
        df = get_kpi_df("kpi_cycle_moyen", "Cycle_Moyen_Journalier",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_cycle_demo(start_date, end_date)))


def load_charge():
    if db_available("kpi_taux_charge"):
        df = get_kpi_df("kpi_taux_charge", "Taux_Charge_Journalier",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_charge_demo(start_date, end_date)))


df_trs    = load_trs()
df_dispo  = load_dispo()
df_perf   = load_perf()
df_cycle  = load_cycle()
df_charge = load_charge()

st.markdown('<div class="header-page">Performance Operationnelle — T\'EleFan</div>',
            unsafe_allow_html=True)

avg_trs     = df_trs["TRS_Pourcent"].mean()             if not df_trs.empty    else 0.0
avg_dispo   = df_dispo["Disponibilite_Pourcent"].mean() if not df_dispo.empty  else 0.0
avg_charge  = df_charge["Taux_Charge_Pourcent"].mean()  if not df_charge.empty else 0.0
avg_cadence = df_perf["Cadence_Pieces_Par_Heure"].mean()if not df_perf.empty   else 0.0

k1, k2, k3, k4 = st.columns(4)
for col, label, value, unit in [
    (k1, "TRS moyen",           avg_trs,     "%"),
    (k2, "Disponibilite moy.",  avg_dispo,   "%"),
    (k3, "Taux de charge moy.", avg_charge,  "%"),
    (k4, "Cadence moyenne",     avg_cadence, "pcs/h"),
]:
    with col:
        st.markdown(
            f'<div class="kpi-box"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value:.1f} {unit}</div></div>',
            unsafe_allow_html=True,
        )

if not df_trs.empty and avg_trs < 30:
    st.info("Note : le TRS est bas car la machine est utilisee uniquement lors des seances de TP "
            "(ETAT_MACHINE_EN_MARCHE = 0 la plupart du temps). C'est coherent avec les donnees reelles.")

st.markdown("---")

# Ligne 1 : TRS jauge + Utilisation ressources + Taux de performance
c1, c2, c3 = st.columns([1, 1.5, 1.5])

with c1:
    st.markdown('<div class="section-title">TRS</div>', unsafe_allow_html=True)
    trs_color = "#C00000" if avg_trs < 70 else ("#FFC000" if avg_trs < 85 else "#4CAF50")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(avg_trs, 1),
        delta={"reference": 85, "increasing": {"color": "#4CAF50"}, "decreasing": {"color": "#C00000"}},
        number={"suffix": " %", "font": {"size": 32, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white", "tickfont": {"color": "white"}},
            "bar": {"color": trs_color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 75],   "color": "#C00000"},
                {"range": [75, 85],  "color": "#FFC000"},
                {"range": [85, 100], "color": "#4CAF50"},
            ],
            "threshold": {"line": {"color": "white", "width": 4}, "thickness": 0.75, "value": 85},
        },
    ))
    fig.update_layout(height=_H, margin=dict(l=20, r=20, t=40, b=20),
                      paper_bgcolor=_BG, font=_FONT)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown('<div class="section-title">Utilisation des ressources (%)</div>', unsafe_allow_html=True)
    if not df_dispo.empty:
        df_d = df_dispo.groupby("Poste")["Disponibilite_Pourcent"].mean().reset_index()\
                       .sort_values("Disponibilite_Pourcent")
        fig = px.bar(df_d, x="Disponibilite_Pourcent", y="Poste", orientation="h",
                     color_discrete_sequence=[_BAR],
                     labels={"Disponibilite_Pourcent": "", "Poste": ""})
        fig.update_layout(height=_H, margin=dict(l=10, r=30, t=10, b=40),
                          xaxis_range=[0, 100], xaxis_ticksuffix="%",
                          plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.2)", color="white")
        fig.update_yaxes(color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee disponibilite pour cette periode.")

with c3:
    st.markdown('<div class="section-title">Taux de performance (cadence pcs/h)</div>', unsafe_allow_html=True)
    if not df_perf.empty:
        df_p = df_perf.groupby("Date_Jour")["Cadence_Pieces_Par_Heure"].mean().reset_index()
        fig = px.line(df_p, x="Date_Jour", y="Cadence_Pieces_Par_Heure", markers=True,
                      labels={"Cadence_Pieces_Par_Heure": "", "Date_Jour": ""})
        fig.update_traces(line_color=_BAR, line_width=2, marker_color=_BAR)
        fig.update_layout(height=_H, margin=dict(l=10, r=20, t=10, b=40),
                          plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.2)", color="white")
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.15)", color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee performance pour cette periode.")

# Ligne 2 : Taux de disponibilite (pleine largeur)
st.markdown('<div class="section-title">Taux de disponibilite par ressource (%)</div>', unsafe_allow_html=True)
if not df_dispo.empty:
    df_d2 = df_dispo.groupby("Poste")["Disponibilite_Pourcent"].mean().reset_index()
    fig = px.bar(df_d2, x="Poste", y="Disponibilite_Pourcent",
                 color_discrete_sequence=[_BAR],
                 labels={"Disponibilite_Pourcent": "", "Poste": ""})
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=60),
                      yaxis_range=[0, 110], yaxis_ticksuffix="%",
                      plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.2)", color="white", tickangle=-30)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.15)", color="white")
    fig.add_hline(y=85, line_dash="dash", line_color="white",
                  annotation_text="Cible 85%", annotation_font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# Ligne 3 : Cycle moyen + Taux de charge
c4, c5 = st.columns(2)

with c4:
    st.markdown('<div class="section-title">Cycle moyen par ressource (s)</div>', unsafe_allow_html=True)
    if not df_cycle.empty:
        df_cy = df_cycle.groupby("Poste")["Cycle_Moyen_Secondes"].mean().reset_index()
        fig = px.bar(df_cy, x="Poste", y="Cycle_Moyen_Secondes",
                     color_discrete_sequence=[_BAR],
                     labels={"Cycle_Moyen_Secondes": "Secondes", "Poste": ""})
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=60),
                          plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
        fig.update_xaxes(color="white", tickangle=-30)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.15)", color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee cycle pour cette periode.")

with c5:
    st.markdown('<div class="section-title">Taux de charge par ressource (%)</div>', unsafe_allow_html=True)
    if not df_charge.empty:
        df_ch = df_charge.groupby("Poste")["Taux_Charge_Pourcent"].mean().reset_index()\
                         .sort_values("Taux_Charge_Pourcent")
        fig = px.bar(df_ch, x="Taux_Charge_Pourcent", y="Poste",
                     orientation="h", color_discrete_sequence=[_BAR],
                     labels={"Taux_Charge_Pourcent": "", "Poste": ""})
        fig.update_layout(height=320, xaxis_range=[0, 100],
                          margin=dict(l=10, r=30, t=10, b=40), xaxis_ticksuffix="%",
                          plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
        fig.update_xaxes(gridcolor="rgba(255,255,255,0.2)", color="white")
        fig.update_yaxes(color="white")
        fig.add_vline(x=80, line_dash="dash", line_color="white",
                      annotation_text="Cible 80%", annotation_font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee taux de charge pour cette periode.")

st.caption("T'EleFan MES 4.0 — Ligne FESTO — IUT Lumiere Lyon 2")
