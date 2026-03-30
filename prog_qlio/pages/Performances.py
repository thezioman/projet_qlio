import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. VÉRIFICATION DE SÉCURITÉ
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Accès restreint : Veuillez vous authentifier sur la page d'accueil.")
    st.stop()

# 2. CONFIGURATION DE LA PAGE
st.set_page_config(layout="wide", page_title="Performance T'Elefan", initial_sidebar_state="expanded")

# 3. CHARTE GRAPHIQUE INFAILLIBLE
st.markdown("""
    <style>
    /* 1. FOND DE LA PAGE FORCÉ EN BLANC (Pour éviter le bug de l'écran noir) */
    .stApp, .main, .block-container { 
        background-color: #ffffff !important; 
    }
    
    /* Masquer l'en-tête par défaut de Streamlit */
    header {visibility: hidden !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    
    /* 2. LE BANDEAU BLEU TOUT EN HAUT */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 120px; 
        background-color: #5fa2ce !important; 
        z-index: 0;
    }
    
    /* On descend légèrement le contenu pour qu'il soit dans le bandeau bleu */
    .block-container {
        padding-top: 1.5rem !important; 
        position: relative;
        z-index: 1;
    }
    
    /* 3. MENU LATÉRAL (GAUCHE) */
    [data-testid="stSidebar"] {
        background-color: #5fa2ce !important; 
    }
    /* Suppression totale de l'espace au dessus de la date */
    [data-testid="stSidebarUserContent"], [data-testid="stSidebarContent"] {
        padding-top: 0rem !important; 
    }
    
    /* Boutons de la sidebar (Visualiser, PDF, Diaporama) */
    [data-testid="stSidebar"] div[data-testid="stButton"] button {
        background-color: #cfcfcf !important;
        color: black !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: bold !important;
        margin-bottom: 5px !important;
    }

    /* 4. BOUTONS DE NAVIGATION (HAUT) : TAILLE ET COULEUR */
    /* On force TOUS les boutons principaux à 75px de haut */
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
        height: 75px !important;
        min-height: 75px !important;
        max-height: 75px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: none !important;
        color: black !important; /* Texte noir forcé contre le mode sombre */
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
        padding: 0 !important;
    }
    
    /* Centrage parfait du texte dans les boutons */
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button p {
        font-size: 16px !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-align: center !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
    }
    
    /* COULEURS DES BOUTONS (Pipetées sur ta maquette) */
    /* 1. Qualité (Vert) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background-color: #8fc280 !important; }
    /* 2. Performance (Bleu + Bordure sombre) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background-color: #7ab4f5 !important; border: 2px solid #234d7d !important; }
    /* 3. Logistique (Rouge brique) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { background-color: #c7605d !important; }
    /* 4. Maintenance (Ocre) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button { background-color: #d4ae65 !important; }
    /* 5. Déconnexion (Gris, forme ovale) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button { background-color: #cfcfcf !important; border-radius: 35px !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. MENU LATÉRAL
with st.sidebar:
    # Encadré Date : Le margin-top négatif force la date à écraser la marge système
    st.markdown("""
    <div style="background-color: #8db4d2; padding: 15px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 30px; margin-top: -30px; color: black;">
        23/01/2025
    </div>
    """, unsafe_allow_html=True)
    
    # Encadré Filtre
    st.markdown("<p style='color: black; font-weight: bold; font-size: 18px; margin-bottom: 5px;'>date :</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #cfcfcf; padding: 10px; text-align: center; font-weight: bold; color: black;">
        7 derniers jours
    </div>
    """, unsafe_allow_html=True)
    
    
    st.markdown('<div style="height: 45vh;"></div>', unsafe_allow_html=True)
    
    # Boutons d'action
    st.button("Visualiser les\ndonnées", use_container_width=True)
    st.button("exporté en pdf", use_container_width=True)
    st.button("mode diaporama", use_container_width=True)


#5. BANDEAU DE NAVIGATION 
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("Qualité", use_container_width=True) : 
     st.switch_page("pages/Qualite.py")
with c2:
    st.button("Performances\nOpérationnel", use_container_width=True)
        

with c3:
    if st.button("Logistique / Flux", use_container_width=True):
        st.switch_page("pages/Logistique.py")

with c4:
    if st.button("Maintenance", use_container_width=True):
        st.switch_page("pages/Maintenance.py")

with c5:
    if st.button("déconnexion", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.switch_page("login.py")


st.write("")
st.write("")

#6. GRAPHIQUES ET DONNÉES
COULEUR_FOND_GRAPHIQUE = "#72a4c2"
COULEUR_DONNEES = "#cc6b49"
COULEUR_TEXTE = "white"

def appliquer_theme_maquette(fig):
    fig.update_layout(
        paper_bgcolor=COULEUR_FOND_GRAPHIQUE,
        plot_bgcolor=COULEUR_FOND_GRAPHIQUE,
        font=dict(color=COULEUR_TEXTE),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', zeroline=False)
    )
    return fig


col_g1, col_g2 = st.columns(2)

with col_g1:
    valeur_trs = 78
    fig_trs = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valeur_trs,
        title={'text': "TRS", 'font': {'color': COULEUR_TEXTE, 'size': 20}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': COULEUR_TEXTE},
            'bar': {'color': "black", 'thickness': 0.2},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [
                {'range': [0, 70], 'color': "#ff0000"},
                {'range': [70, 85], 'color': "#ffc000"},
                {'range': [85, 100], 'color': "#00b050"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': valeur_trs}
        }
    ))
    fig_trs = appliquer_theme_maquette(fig_trs)
    fig_trs.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_trs, use_container_width=True)

with col_g2:
    df_titre = pd.DataFrame({
        "Opération": ["opération 1", "opération 2", "opération 3", "opération 4", "opération 5"],
        "Valeur": [60, 82, 50, 78, 52]
    })
    fig_titre = px.bar(df_titre, x="Opération", y="Valeur", title="Cycle moyen")
    fig_titre.update_traces(marker_color=COULEUR_DONNEES, width=0.4)
    fig_titre = appliquer_theme_maquette(fig_titre)
    fig_titre.update_layout(height=300, yaxis_range=[0, 100], yaxis_ticksuffix="%")
    st.plotly_chart(fig_titre, use_container_width=True)


col_g3, col_g4 = st.columns(2)

with col_g3:
    df_use = pd.DataFrame({
        "Ressource": ["ressource 1", "ressource 2", "ressource 3", "ressource 4", "ressource 5"],
        "Utilisation": [62, 85, 28, 52, 78]
    })
    fig_use = px.bar(df_use, x="Utilisation", y="Ressource", orientation='h', title="Utilisation des ressources")
    fig_use.update_traces(marker_color=COULEUR_DONNEES, width=0.4)
    fig_use = appliquer_theme_maquette(fig_use)
    fig_use.update_layout(height=300, xaxis_range=[0, 100], xaxis_ticksuffix="%")
    st.plotly_chart(fig_use, use_container_width=True)

with col_g4:
    df_perf = pd.DataFrame({
        "Jour": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
        "Performance": [75, 85, 88, 70, 65, 64, 68]
    })
    fig_perf = px.line(df_perf, x="Jour", y="Performance", title="Taux de performance")
    fig_perf.update_traces(line_color=COULEUR_DONNEES, line_width=4)
    fig_perf = appliquer_theme_maquette(fig_perf)
    fig_perf.update_layout(height=300, yaxis_range=[0, 100], yaxis_ticksuffix="%")
    st.plotly_chart(fig_perf, use_container_width=True)


df_dispo = pd.DataFrame({
    "Ressource": [f"ressource {i}" for i in range(1, 11)],
    "Disponibilité": [45, 68, 96, 12, 54, 65, 78, 64, 32, 91]
})
fig_dispo = px.bar(df_dispo, x="Ressource", y="Disponibilité", title="Taux de disponibilité")
fig_dispo.update_traces(marker_color=COULEUR_DONNEES, width=0.3)
fig_dispo = appliquer_theme_maquette(fig_dispo)
fig_dispo.update_layout(height=400, yaxis_range=[0, 120], yaxis_ticksuffix="%")
st.plotly_chart(fig_dispo, use_container_width=True)
