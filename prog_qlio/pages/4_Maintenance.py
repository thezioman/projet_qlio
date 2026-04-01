import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import check_auth, render_navbar, render_sidebar_filters, handle_slideshow
from db import get_kpi_df, db_available
import demo_data as demo

st.set_page_config(layout="wide", page_title="Maintenance – T'EleFan",
                   initial_sidebar_state="expanded")

check_auth(allowed_roles=["admin", "manager_ops"])

handle_slideshow("Maintenance", st.session_state.get("slideshow_interval", 15))

st.markdown("""
<style>
.stApp {background-color: #FEF5EC;}
.header-page {
    background: #E67E22; color: white; padding: 12px 20px;
    border-radius: 8px; font-family: Arial; font-size: 20px;
    font-weight: bold; margin-bottom: 18px;
}
.kpi-box {
    background: #E67E22; color: white; padding: 14px 18px;
    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); margin-bottom: 12px;
}
.kpi-label {font-size: 12px; color: rgba(255,255,255,0.8); font-family: Arial;}
.kpi-value {font-size: 26px; font-weight: bold; color: white; font-family: Arial;}
.section-title {
    color: white; background: rgba(230,126,34,0.85); padding: 6px 12px;
    border-radius: 6px; font-family: Arial; font-size: 13px;
    font-weight: bold; margin-bottom: 4px; text-align: center;
}
</style>
""", unsafe_allow_html=True)

render_navbar(active="Maintenance")

start_date, end_date, resource_ids = render_sidebar_filters()

_BG   = "#E67E22"
_CARD = "rgba(255,255,255,0.12)"
_BAR  = "#0055c7"
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


def load_fiabilite():
    if db_available("kpi_fiabilite"):
        df = get_kpi_df("kpi_fiabilite", "Fiabilite_Journaliere",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return _filter_r(_add_poste(demo.get_fiabilite_demo(start_date, end_date)))


def load_rebuts():
    if db_available("kpi_rebuts"):
        df = get_kpi_df("kpi_rebuts", "Rebuts_Journaliers",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return _add_poste(_filter_r(df))
    return demo.get_rebuts_demo(start_date, end_date)


df_fiab   = load_fiabilite()
df_rebuts = load_rebuts()

st.markdown('<div class="header-page">Maintenance — T\'EleFan</div>', unsafe_allow_html=True)

total_erreurs = df_rebuts["Nb_Rebuts"].sum()       if not df_rebuts.empty else 0
avg_mtbf      = df_fiab["MTBF_Minutes"].mean()     if not df_fiab.empty  else 0.0
avg_mttr      = df_fiab["MTTR_Minutes"].mean()     if not df_fiab.empty  else 0.0
nb_ressources = df_fiab["Poste"].nunique()         if not df_fiab.empty  else 0

k1, k2, k3, k4 = st.columns(4)
for col, label, value, unit in [
    (k1, "Nombre d'erreurs",  total_erreurs, ""),
    (k2, "MTBF moyen",        avg_mtbf,      "min"),
    (k3, "MTTR moyen",        avg_mttr,      "min"),
    (k4, "Ressources suivies", nb_ressources, ""),
]:
    with col:
        st.markdown(
            f'<div class="kpi-box"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value:.0f} {unit}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

col_gauche, col_droite = st.columns(2)

with col_gauche:
    # KPI nombre d'erreurs — indicateur
    st.markdown('<div class="section-title">Nombre d\'erreurs total</div>', unsafe_allow_html=True)
    fig = go.Figure(go.Indicator(
        mode="number",
        value=int(total_erreurs),
        number={"font": {"size": 64, "color": "white"}},
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20),
                      paper_bgcolor=_BG, font=_FONT)
    st.plotly_chart(fig, use_container_width=True)

    # Duree moyenne d'indisponibilite par ressource (MTTR)
    st.markdown('<div class="section-title">Duree moyenne d\'indisponibilite par ressource (MTTR, min)</div>',
                unsafe_allow_html=True)
    if not df_fiab.empty:
        df_mttr = df_fiab.groupby("Poste")["MTTR_Minutes"].mean().reset_index()\
                         .sort_values("MTTR_Minutes")
        fig = go.Figure(go.Bar(
            x=df_mttr["MTTR_Minutes"], y=df_mttr["Poste"],
            orientation="h", marker_color=_BAR,
        ))
        fig.update_layout(height=_H, margin=dict(l=10, r=20, t=10, b=40),
                          plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
        fig.update_xaxes(color="white", tickfont=dict(color="white"))
        fig.update_yaxes(color="white", tickfont=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee fiabilite pour cette periode.")

with col_droite:
    # Repartition erreurs par ressource (barres + courbe cumul)
    st.markdown('<div class="section-title">Repartitions d\'erreurs par ressource</div>',
                unsafe_allow_html=True)
    if not df_rebuts.empty:
        df_r = df_rebuts.groupby("Poste")["Nb_Rebuts"].sum().reset_index()\
                        .sort_values("Nb_Rebuts", ascending=False)
        total = df_r["Nb_Rebuts"].sum()
        df_r["Cumul_%"] = (df_r["Nb_Rebuts"].cumsum() / total * 100).round(1) if total > 0 else 0

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_r["Poste"], y=df_r["Nb_Rebuts"],
                             name="Nb erreurs", marker_color=_BAR, yaxis="y1"))
        fig.add_trace(go.Scatter(x=df_r["Poste"], y=df_r["Cumul_%"],
                                 mode="lines+markers", name="Cumul %",
                                 line=dict(color="#9c9c9c", width=3), yaxis="y2"))
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=60, t=10, b=60),
            yaxis=dict(color="white", tickfont=dict(color="white"),
                       gridcolor="rgba(255,255,255,0.15)"),
            yaxis2=dict(overlaying="y", side="right", range=[0, 110],
                        ticksuffix="%", color="white", tickfont=dict(color="white"),
                        showgrid=False),
            legend=dict(orientation="h", y=-0.3, font=dict(color="white")),
            plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT,
        )
        fig.update_xaxes(color="white", tickfont=dict(color="white"), tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee erreurs pour cette periode.")

    # Repartition par type d'erreur
    st.markdown('<div class="section-title">Repartitions par type d\'erreur</div>',
                unsafe_allow_html=True)
    if not df_rebuts.empty:
        df_t = df_rebuts.groupby("Description_Erreur")["Nb_Rebuts"].sum().reset_index()\
                        .sort_values("Nb_Rebuts", ascending=False)
        fig = go.Figure(go.Bar(
            x=df_t["Description_Erreur"], y=df_t["Nb_Rebuts"],
            marker_color=_BAR,
        ))
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=80),
                          plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
        fig.update_xaxes(color="white", tickfont=dict(color="white"),
                         tickangle=-30)
        fig.update_yaxes(color="white", tickfont=dict(color="white"),
                         gridcolor="rgba(255,255,255,0.15)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee types d'erreur pour cette periode.")

st.caption("T'EleFan MES 4.0 — Ligne FESTO — IUT Lumiere Lyon 2")
