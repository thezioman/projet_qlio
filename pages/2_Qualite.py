import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import check_auth, render_navbar, render_sidebar_filters, handle_slideshow
from db import get_kpi_df, db_available
import demo_data as demo

st.set_page_config(layout="wide", page_title="Qualite – T'EleFan",
                   initial_sidebar_state="expanded")

check_auth(allowed_roles=["admin", "manager_ops", "manager_supply"])

handle_slideshow("Qualite", st.session_state.get("slideshow_interval", 15))

st.markdown("""
<style>
.stApp {background-color: #EEF7EE;}
.header-page {
    background: #4CAF50; color: white; padding: 12px 20px;
    border-radius: 8px; font-family: Arial; font-size: 20px;
    font-weight: bold; margin-bottom: 18px;
}
.kpi-box {
    background: #4CAF50; color: white; padding: 14px 18px;
    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); margin-bottom: 12px;
}
.kpi-label {font-size: 12px; color: rgba(255,255,255,0.8); font-family: Arial;}
.kpi-value {font-size: 26px; font-weight: bold; color: white; font-family: Arial;}
.section-title {
    color: white; background: rgba(76,175,80,0.85); padding: 6px 12px;
    border-radius: 6px; font-family: Arial; font-size: 13px;
    font-weight: bold; margin-bottom: 4px; text-align: center;
}
</style>
""", unsafe_allow_html=True)

render_navbar(active="Qualite")

start_date, end_date, resource_ids = render_sidebar_filters()

_BG   = "#4CAF50"
_CARD = "rgba(255,255,255,0.12)"
_BAR  = "#A768B4"
_FONT = dict(color="white", family="Arial")
_H    = 340

POSTES_QUALITE = [1, 2, 3, 5, 7, 8]


def _add_poste(df):
    if "ID_Ressource" in df.columns and "Poste" not in df.columns:
        df = df.copy()
        df["Poste"] = df["ID_Ressource"].apply(lambda x: f"Poste {x}")
    return df


def _filter_r(df):
    if "ID_Ressource" in df.columns and resource_ids:
        return df[df["ID_Ressource"].isin(resource_ids)]
    return df


def load_qualite():
    if db_available("kpi_qualite"):
        df = get_kpi_df("kpi_qualite", "Qualite_Journaliere",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_qualite_demo(start_date, end_date)))


def load_rebuts():
    if db_available("kpi_rebuts"):
        df = get_kpi_df("kpi_rebuts", "Rebuts_Journaliers",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return demo.get_rebuts_demo(start_date, end_date)


def load_fiabilite():
    if db_available("kpi_fiabilite"):
        df = get_kpi_df("kpi_fiabilite", "Fiabilite_Journaliere",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_fiabilite_demo(start_date, end_date)))


df_qual   = load_qualite()
df_rebuts = load_rebuts()
df_fiab   = load_fiabilite()

st.markdown('<div class="header-page">Indicateurs Qualite — T\'EleFan</div>',
            unsafe_allow_html=True)

avg_qual  = df_qual["Taux_Qualite_Pourcent"].mean()  if not df_qual.empty  else 0.0
total_reb = df_rebuts["Nb_Rebuts"].sum()             if not df_rebuts.empty else 0
avg_mtbf  = df_fiab["MTBF_Minutes"].mean()           if not df_fiab.empty  else 0.0
avg_mttr  = df_fiab["MTTR_Minutes"].mean()           if not df_fiab.empty  else 0.0

k1, k2, k3, k4 = st.columns(4)
for col, label, value, unit in [
    (k1, "Taux de qualite moy.", avg_qual,  "%"),
    (k2, "Total rebuts",         total_reb, "pcs"),
    (k3, "MTBF moyen",           avg_mtbf,  "min"),
    (k4, "MTTR moyen",           avg_mttr,  "min"),
]:
    with col:
        st.markdown(
            f'<div class="kpi-box"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value:.1f} {unit}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# Ligne 1 : Qualite jauge + MTBF/MTTR
c1, c2 = st.columns([1, 1.5])

with c1:
    st.markdown('<div class="section-title">Taux de Qualite (%)</div>', unsafe_allow_html=True)
    qual_color = "#C00000" if avg_qual < 75 else ("#FFC000" if avg_qual < 85 else "#92D050")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(avg_qual, 1),
        delta={"reference": 85, "increasing": {"color": "#92D050"}, "decreasing": {"color": "#C00000"}},
        number={"suffix": " %", "font": {"size": 32, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white", "tickfont": {"color": "white"}},
            "bar": {"color": qual_color, "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 75],   "color": "#C00000"},
                {"range": [75, 85],  "color": "#FFC000"},
                {"range": [85, 100], "color": "#92D050"},
            ],
            "threshold": {"line": {"color": "white", "width": 4}, "thickness": 0.75, "value": 85},
        },
    ))
    fig.update_layout(height=_H, margin=dict(l=20, r=20, t=40, b=20),
                      paper_bgcolor=_BG, font=_FONT)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown('<div class="section-title">MTBF / MTTR par ressource (minutes)</div>', unsafe_allow_html=True)
    if not df_fiab.empty:
        df_f = df_fiab.groupby("Poste")[["MTBF_Minutes", "MTTR_Minutes"]].mean().reset_index()
        # Cap MTBF a 500 min pour la lisibilite (valeurs aberrantes sur longues periodes)
        df_f["MTBF_Minutes"] = df_f["MTBF_Minutes"].clip(upper=500)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_f["Poste"], y=df_f["MTBF_Minutes"],
                             name="MTBF (min)", marker_color=_BAR))
        fig.add_trace(go.Bar(x=df_f["Poste"], y=df_f["MTTR_Minutes"],
                             name="MTTR (min)", marker_color="#7B3FA0"))
        fig.update_layout(barmode="group", height=_H,
                          margin=dict(l=10, r=10, t=10, b=60),
                          legend=dict(orientation="h", yanchor="bottom", y=-0.35,
                                      font=dict(color="white")),
                          plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
        fig.update_xaxes(color="white", tickfont=dict(color="white"), tickangle=-30)
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.15)", color="white",
                         tickfont=dict(color="white"), title="minutes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee fiabilite pour cette periode.")

# Ligne 2 : Rebuts Pareto (pleine largeur)
st.markdown('<div class="section-title">Repartitions par type d\'erreur (Pareto)</div>',
            unsafe_allow_html=True)
if not df_rebuts.empty:
    df_p = df_rebuts.groupby("Description_Erreur")["Nb_Rebuts"].sum().reset_index()\
                    .sort_values("Nb_Rebuts", ascending=False)
    total = df_p["Nb_Rebuts"].sum()
    df_p["Cumul_%"] = (df_p["Nb_Rebuts"].cumsum() / total * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_p["Description_Erreur"], y=df_p["Nb_Rebuts"],
                         name="Nb rebuts", marker_color=_BAR, yaxis="y1"))
    fig.add_trace(go.Scatter(x=df_p["Description_Erreur"], y=df_p["Cumul_%"],
                             mode="lines+markers", name="Cumul %",
                             line=dict(color="white", width=2), yaxis="y2"))
    fig.update_layout(
        height=380,
        margin=dict(l=10, r=60, t=10, b=80),
        yaxis=dict(gridcolor="rgba(255,255,255,0.15)", color="white", title="Nombre rebuts"),
        yaxis2=dict(overlaying="y", side="right", range=[0, 110],
                    ticksuffix="%", color="white", title="Cumul %"),
        legend=dict(orientation="h", y=-0.3, font=dict(color="white")),
        plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT,
    )
    fig.update_xaxes(color="white", tickfont=dict(color="white"), tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnee rebuts pour cette periode.")


st.caption("T'EleFan MES 4.0 — Ligne FESTO — IUT Lumiere Lyon 2")
