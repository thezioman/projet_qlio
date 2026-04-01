import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import check_auth, render_navbar, render_sidebar_filters, handle_slideshow
from db import get_kpi_df, db_available
import demo_data as demo

st.set_page_config(layout="wide", page_title="Logistique – T'EleFan",
                   initial_sidebar_state="expanded")

check_auth(allowed_roles=["admin", "manager_supply"])

handle_slideshow("Logistique", st.session_state.get("slideshow_interval", 15))

st.markdown("""
<style>
.stApp {background-color: #FEF2F2;}
.header-page {
    background: #C0392B; color: white; padding: 12px 20px;
    border-radius: 8px; font-family: Arial; font-size: 20px;
    font-weight: bold; margin-bottom: 18px;
}
.kpi-box {
    background: #C0392B; color: white; padding: 14px 18px;
    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); margin-bottom: 12px;
}
.kpi-label {font-size: 12px; color: rgba(255,255,255,0.8); font-family: Arial;}
.kpi-value {font-size: 26px; font-weight: bold; color: white; font-family: Arial;}
.section-title {
    color: white; background: rgba(192,57,43,0.85); padding: 6px 12px;
    border-radius: 6px; font-family: Arial; font-size: 13px;
    font-weight: bold; margin-bottom: 4px; text-align: center;
}
.otd-ok  {background:#DFFFD8;color:#375623;padding:3px 8px;border-radius:4px;font-weight:bold;font-size:12px;}
.otd-nok {background:#FFDEDE;color:#7B0000;padding:3px 8px;border-radius:4px;font-weight:bold;font-size:12px;}
</style>
""", unsafe_allow_html=True)

render_navbar(active="Logistique")

start_date, end_date, resource_ids = render_sidebar_filters(show_machine=False)

_BG   = "#C0392B"
_CARD = "rgba(255,255,255,0.12)"
_FONT = dict(color="white", family="Arial")
_H    = 340


def load_lead_time():
    if db_available("kpi_lead_time"):
        df = get_kpi_df("kpi_lead_time", "Lead_Time_Journalier",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return df
    return demo.get_lead_time_demo(start_date, end_date)


def load_otd():
    if db_available("kpi_otd"):
        df = get_kpi_df("kpi_otd", "OTD_Journalier",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            return df
    return demo.get_otd_demo(start_date, end_date)


def load_wip():
    if db_available("kpi_wip"):
        df = get_kpi_df("kpi_wip", "WIP_Journalier",
                        start_date=start_date, end_date=end_date)
        if df is not None:
            if "Poste" not in df.columns and "ID_Ressource" in df.columns:
                df["Poste"] = df["ID_Ressource"].apply(lambda x: f"Poste {x}")
            return df
    return demo.get_wip_demo(start_date, end_date)


def load_stock():
    if db_available("kpi_stock"):
        df = get_kpi_df("kpi_stock", "Stock_Actuel", date_col=None)
        if df is not None:
            return df
    return demo.get_stock_demo()


df_lt    = load_lead_time()
df_otd   = load_otd()
df_wip   = load_wip()
df_stock = load_stock()

st.markdown('<div class="header-page">Logistique / Flux — T\'EleFan</div>',
            unsafe_allow_html=True)

avg_lt  = df_lt["Lead_Time_Minutes"].mean()          if not df_lt.empty  else 0.0
avg_otd = df_otd["OTD_Pourcent"].mean()              if not df_otd.empty else 0.0
tot_cmd = df_otd["Total_Commandes"].sum()             if not df_otd.empty else 0
avg_wip = df_wip["Taux_Occupation_Pourcent"].mean()  if not df_wip.empty else 0.0

k1, k2, k3, k4 = st.columns(4)
for col, label, value, unit in [
    (k1, "Lead Time moyen",     avg_lt,  "min"),
    (k2, "OTD moyen",           avg_otd, "%"),
    (k3, "Commandes analysees", tot_cmd, ""),
    (k4, "Occupation WIP",      avg_wip, "%"),
]:
    with col:
        st.markdown(
            f'<div class="kpi-box"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value:.0f} {unit}</div></div>',
            unsafe_allow_html=True,
        )

if avg_otd == 0 and not df_otd.empty:
    st.markdown(
        "<div style='background:#FFF3CD;color:#7B5800;border:1px solid #FFCC00;"
        "border-radius:6px;padding:10px 14px;font-size:13px;margin-bottom:8px;'>"
        "<b>OTD = 0%</b> : dans les donnees reelles, toutes les commandes sont terminees "
        "apres la date planifiee (DATE_FIN_COMMANDE > DATE_FIN_PLANIFIEE). "
        "C'est une caracteristique des donnees FESTO."
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# Tableau OTD
st.markdown('<div class="section-title">Suivi des commandes — OTD</div>', unsafe_allow_html=True)
if not df_otd.empty:
    df_show = df_otd[["Date_Jour", "Total_Commandes", "Commandes_A_L_Heure", "OTD_Pourcent"]].copy()
    df_show.columns = ["Date", "Total commandes", "A l'heure", "OTD %"]
    df_show["OTD %"] = df_show["OTD %"].round(1)
    st.dataframe(df_show.sort_values("Date", ascending=False).head(15).reset_index(drop=True),
                 use_container_width=True, height=220)

st.markdown("---")

# Ligne 1 : WIP Heatmap + Stock Pareto
c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="section-title">Heatmap WIP — Taux d\'occupation par ressource</div>',
                unsafe_allow_html=True)
    if not df_wip.empty:
        df_h = df_wip.groupby(["Date_Jour", "Poste"])["Taux_Occupation_Pourcent"].mean().reset_index()
        if not df_h.empty:
            pivot = df_h.pivot(index="Poste", columns="Date_Jour",
                               values="Taux_Occupation_Pourcent")
            fig = px.imshow(pivot,
                            color_continuous_scale=["#1a5276", "#5dade2", "#aed6f1"],
                            zmin=0, zmax=100,
                            labels={"color": "Occupation %"},
                            aspect="auto")
            fig.update_layout(height=_H, margin=dict(l=10, r=60, t=10, b=60),
                              paper_bgcolor=_BG, font=_FONT,
                              coloraxis_colorbar=dict(
                                  tickfont=dict(color="white"),
                                  title=dict(font=dict(color="white"))))
            fig.update_xaxes(color="white", tickangle=-30)
            fig.update_yaxes(color="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Donnees WIP insuffisantes.")
    else:
        st.info("Aucune donnee WIP pour cette periode.")

with c4:
    st.markdown('<div class="section-title">Stock par reference (Pareto)</div>', unsafe_allow_html=True)
    if not df_stock.empty:
        df_s = df_stock.sort_values("Quantite_Totale", ascending=False).copy()
        total_s = df_s["Quantite_Totale"].sum()
        df_s["Cumul_%"] = (df_s["Quantite_Totale"].cumsum() / total_s * 100).round(1)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_s["Description_Piece"], y=df_s["Quantite_Totale"],
                             name="Stock", marker_color="#5dade2", yaxis="y1"))
        fig.add_trace(go.Scatter(x=df_s["Description_Piece"], y=df_s["Cumul_%"],
                                 mode="lines+markers", name="Cumule",
                                 line=dict(color="white", width=2), yaxis="y2"))
        fig.update_layout(
            height=_H, margin=dict(l=10, r=60, t=10, b=80),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.15)", title="Quantite"),
            yaxis2=dict(overlaying="y", side="right", range=[0, 110],
                        ticksuffix="%", color="white", title="Cumul %"),
            legend=dict(orientation="h", y=-0.35, font=dict(color="white")),
            plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT,
        )
        fig.update_xaxes(color="white", tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnee stock.")

# Ligne 2 : Lead Time distribution
st.markdown('<div class="section-title">Lead Time par commande (minutes)</div>', unsafe_allow_html=True)
if not df_lt.empty:
    # Filtre les valeurs aberrantes (> 1500 min)
    df_lt_clean = df_lt[df_lt["Lead_Time_Minutes"] <= 1500].copy()
    if df_lt_clean.empty:
        df_lt_clean = df_lt.copy()

    fig = px.box(df_lt_clean, x="Date_Jour", y="Lead_Time_Minutes",
                 labels={"Lead_Time_Minutes": "Lead Time (min)", "Date_Jour": ""},
                 color_discrete_sequence=["#5dade2"])
    df_trend = df_lt_clean.groupby("Date_Jour")["Lead_Time_Minutes"].mean().reset_index()
    fig.add_scatter(x=df_trend["Date_Jour"], y=df_trend["Lead_Time_Minutes"],
                    mode="lines", name="Moyenne",
                    line=dict(color="white", width=2, dash="dot"))
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=60),
                      plot_bgcolor=_CARD, paper_bgcolor=_BG, font=_FONT)
    fig.update_xaxes(color="white", tickangle=-30)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.15)", color="white")
    st.plotly_chart(fig, use_container_width=True)
    if len(df_lt) > len(df_lt_clean):
        st.caption(f"Note : {len(df_lt) - len(df_lt_clean)} valeurs > 1500 min exclues pour la lisibilite.")
else:
    st.info("Aucune donnee lead time pour cette periode.")

st.caption("T'EleFan MES 4.0 — Ligne FESTO — IUT Lumiere Lyon 2")
