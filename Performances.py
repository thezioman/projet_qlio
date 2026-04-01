import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. SÉCURITÉ & CONFIG ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("🔒 Veuillez vous connecter depuis la page Login.")
    st.stop()

st.set_page_config(layout="wide", page_title="Performance T'Elefan")

# --- 2. STYLE VISUEL (LE BLEU DE LA MAQUETTE) ---
st.markdown("""
    <style>
    /* Bandeau supérieur en BLEU (#4da6ff) */
    .stAppHeader {
        background-color: #5B9BD5;
    }
    
    /* Titre Principal style "Encadré Bleu" */
    .titre-dashboard {
        background-color: #5B9BD5;
        color: white;
        padding: 15px;
        text-align: center;
        border-radius: 5px;
        font-family: Arial, sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* Fond de page gris très clair pour faire ressortir les graphiques */
    .stApp {
        background-color: #F4F7FC;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNEXION BDD ---
def get_data(query):
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="root",
            database="python_auth_db", port=3307
        )
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        # Si la BDD est vide ou éteinte, on retourne un DataFrame vide pour ne pas faire planter
        return pd.DataFrame()

# --- 4. AFFICHAGE DU TITRE ---
col_titre1, col_titre2 = st.columns([4, 1])
with col_titre1:
    st.markdown('<div class="titre-dashboard">Rapport de performance T’ELE FAN</div>', unsafe_allow_html=True)
with col_titre2:
    # Petit encadré année comme sur la maquette
    st.markdown('<div class="titre-dashboard" style="background-color:#70AD47;">2025</div>', unsafe_allow_html=True)

st.markdown("### Indicateurs de la Performance Opérationnelle")

# --- 5. LIGNE DU HAUT (3 GRAPHIQUES) ---
c1, c2, c3 = st.columns(3)

# --- A. TAUX DE DISPONIBILITÉ (Barres) ---
with c1:
    st.markdown("**Taux de Disponibilité**")
    # SQL : On compte le temps 'Busy' vs le temps total par machine
    # (Ici simulation si BDD vide pour l'affichage maquette)
    df_dispo = get_data("SELECT ResourceID, COUNT(*) as Total FROM tblmachinereport GROUP BY ResourceID")
    
    if df_dispo.empty:
        # Données fictives pour que tu voies le résultat visuel immédiat
        df_dispo = pd.DataFrame({
            "Machine": ["Magasin", "Presse", "Robot", "Contrôle"],
            "Disponibilité": [95, 88, 76, 92]
        })
        fig_dispo = px.bar(df_dispo, x="Machine", y="Disponibilité", 
                           color_discrete_sequence=['#5B9BD5']) # Bleu maquette
        fig_dispo.update_layout(yaxis_range=[0, 100], margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_dispo, use_container_width=True)

# --- B. TAUX DE PERFORMANCE (Courbe) ---
with c2:
    st.markdown("**Taux de Performance (Cadence)**")
    df_perf = pd.DataFrame({
        "Mois": ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin"],
        "Production": [200, 450, 500, 750, 800, 950]
    })
    fig_perf = px.line(df_perf, x="Mois", y="Production", markers=True)
    fig_perf.update_traces(line_color='#5B9BD5', line_width=3)
    fig_perf.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_perf, use_container_width=True)

# --- C. TRS (Jauge Circulaire) ---
with c3:
    st.markdown("**TRS (Taux de Rendement Synthétique)**")
    # Valeur cible définie dans le cahier des charges (Source 47)
    valeur_trs = 78 # Exemple dynamique
    
    fig_trs = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valeur_trs,
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 70], 'color': "#C00000"},   # Rouge (Source 47)
                {'range': [70, 85], 'color': "#FFC000"},  # Orange (Source 47)
                {'range': [85, 100], 'color': "#92D050"}  # Vert (Source 47)
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': valeur_trs}
        }
    ))
    fig_trs.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_trs, use_container_width=True)

# --- 6. LIGNE DU BAS (2 GRAPHIQUES) ---
c4, c5 = st.columns(2)

# --- D. CYCLE MOYEN (Histogramme Bleu) ---
with c4:
    st.markdown("**Cycle moyen (par poste)**")
    df_cycle = pd.DataFrame({
        "Poste": ["P1", "P2", "P3", "P4", "P5", "P6"],
        "Temps (s)": [12, 15, 18, 22, 14, 30]
    })
    fig_cycle = px.bar(df_cycle, x="Poste", y="Temps (s)", 
                       color_discrete_sequence=['#4472C4']) # Bleu foncé
    fig_cycle.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_cycle, use_container_width=True)

# --- E. UTILISATION RESSOURCES (Barres Horizontales) ---
with c5:
    st.markdown("**Utilisation des ressources**")
    df_use = pd.DataFrame({
        "Ressource": ["Convoyeur", "Bras Robot", "Capteur Vision", "Presse H"],
        "Utilisation %": [80, 65, 45, 90]
    })
    # Barres horizontales (orientation='h')
    fig_use = px.bar(df_use, x="Utilisation %", y="Ressource", orientation='h',
                     color_discrete_sequence=['#4472C4'])
    fig_use.update_layout(xaxis_range=[0, 100], margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_use, use_container_width=True)