import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. VÉRIFICATION DE SÉCURITÉ ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Accès restreint : Veuillez vous authentifier sur la page d'accueil.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Logistique T'Elefan", initial_sidebar_state="expanded")

# --- 3. CHARTE GRAPHIQUE INFAILLIBLE (CSS) ---
COULEUR_BANDEAU = "#b93030"

st.markdown(f"""
    <style>
    /* FOND DE LA PAGE EN BLANC */
    .stApp, .main, .block-container {{ background-color: #ffffff !important; }}
    header {{visibility: hidden !important;}}
    [data-testid="stSidebarNav"] {{display: none !important;}}
    
    /* LE BANDEAU ROUGE TOUT EN HAUT */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 120px; 
        background-color: {COULEUR_BANDEAU} !important; 
        z-index: 0;
    }}
    
    .block-container {{
        padding-top: 1.5rem !important; 
        position: relative;
        z-index: 1;
    }}
    
    /* MENU LATÉRAL (GAUCHE) EN ROUGE */
    [data-testid="stSidebar"] {{
        background-color: {COULEUR_BANDEAU} !important; 
    }}
    [data-testid="stSidebarUserContent"], [data-testid="stSidebarContent"] {{
        padding-top: 0rem !important; 
    }}
    
    /* Boutons de la sidebar */
    [data-testid="stSidebar"] div[data-testid="stButton"] button {{
        background-color: #cfcfcf !important;
        color: black !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: bold !important;
        margin-bottom: 5px !important;
    }}

    /* BOUTONS DE NAVIGATION (HAUT) */
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {{
        height: 75px !important;
        min-height: 75px !important;
        max-height: 75px !important;
        width: 100% !important;
        border-radius: 10px !important;
        border: none !important;
        color: black !important; 
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
        padding: 0 !important;
    }}
    
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button p {{
        font-size: 16px !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-align: center !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
    }}
    
    /* COULEURS DES BOUTONS (LOGISTIQUE ACTIF) */
    /* 1. Qualité */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{ background-color: #8fc280 !important; }}
    /* 2. Performance */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{ background-color: #7ab4f5 !important; }}
    /* 3. Logistique (ACTIF -> Bordure sombre) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {{ background-color: {COULEUR_BANDEAU} !important; border: 2px solid #731e1e !important; color: white !important; }}
    /* 4. Maintenance */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {{ background-color: #d4ae65 !important; }}
    /* 5. Déconnexion */
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {{ background-color: #cfcfcf !important; border-radius: 35px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.markdown(f"""
    <div style="background-color: #d65858; padding: 15px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 30px; margin-top: -30px; color: black;">
        23/01/2025
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: black; font-weight: bold; font-size: 18px; margin-bottom: 5px;'>date :</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: #cfcfcf; padding: 10px; text-align: center; font-weight: bold; color: black;">
        7 derniers jours
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="height: 45vh;"></div>', unsafe_allow_html=True)
    
    st.button("Visualiser les\ndonnées", use_container_width=True)
    st.button("exporté en pdf", use_container_width=True)
    st.button("mode diaporama", use_container_width=True)

# --- 5. BANDEAU DE NAVIGATION (HAUT) ---
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("Qualité", use_container_width=True) :
        st.switch_page("pages/Qualite.py")
with c2:
    if st.button("Performances\nOpérationnel", use_container_width=True):
        st.switch_page("pages/Performances.py")

with c3:
    st.button("Logistique / Flux", use_container_width=True)

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

# --- 6. GRAPHIQUES ET DONNÉES ---
COULEUR_FOND_GRAPHIQUE = "#DC4949"
COULEUR_PRIMAIRE = "#0B8585"
COULEUR_SECONDAIRE = "#B7B7B7"
COULEUR_TEXTE = "white"

def appliquer_theme_maquette(fig):
    fig.update_layout(
        paper_bgcolor=COULEUR_FOND_GRAPHIQUE,
        plot_bgcolor=COULEUR_FOND_GRAPHIQUE,
        font=dict(color=COULEUR_TEXTE),
        margin=dict(l=30, r=30, t=40, b=30),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', zeroline=False)
    )
    return fig

# ---------------------------------------------------------
# LIGNE 1 : TABLEAU DE COMMANDES (Pleine largeur)
# ---------------------------------------------------------
df_commandes = pd.DataFrame({
    "numéro de commande": [1, 2, 3, 4, 5],
    "quantité": [5, 4, 3, 2, 1],
    "date de livraison promise": ["21/01/2026", "22/01/2026", "23/01/2026", "24/01/2026", "25/01/2026"],
    "date de livraison réalisé": ["21/01/2026", "25/01/2026", "23/01/2026", "25/02/2026", "25/01/2026"],
    "OTD": ["OK", "NOK", "OK", "NOK", "OK"]
})

# Définition des couleurs conditionnelles pour la colonne OTD
couleurs_fond_otd = ['#d4edda' if val == 'OK' else '#f8d7da' for val in df_commandes['OTD']]
couleurs_texte_otd = ['#155724' if val == 'OK' else '#721c24' for val in df_commandes['OTD']]

fig_table = go.Figure(data=[go.Table(
    header=dict(
        values=list(df_commandes.columns),
        fill_color='#a33030', # Rouge sombre pour l'en-tête
        align='left',
        font=dict(color='white', size=14, family="Arial")
    ),
    cells=dict(
        values=[df_commandes[col] for col in df_commandes.columns],
        # Les 4 premières colonnes ont un fond rouge clair, la dernière s'adapte selon OK/NOK
        fill_color=[
            ['#c45656']*5, ['#c45656']*5, ['#c45656']*5, ['#c45656']*5, couleurs_fond_otd
        ],
        align='left',
        font=dict(color=[['white']*5, ['white']*5, ['white']*5, ['white']*5, couleurs_texte_otd], size=14)
    )
)])
fig_table = appliquer_theme_maquette(fig_table)
fig_table.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_table, use_container_width=True)

# ---------------------------------------------------------
# LIGNE 2 : HEATMAP (Gauche) & GRAPHIQUE MIXTE (Droite)
# ---------------------------------------------------------
col_g1, col_g2 = st.columns(2)

with col_g1:
    # Génération d'une Heatmap de démonstration 12x24
    np.random.seed(42)
    z_data = np.random.rand(12, 24)
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=z_data,
        colorscale=[[0.0, COULEUR_FOND_GRAPHIQUE], [0.5, COULEUR_SECONDAIRE], [1.0, COULEUR_PRIMAIRE]],
        colorbar=dict(title=dict(text="Taux d'occupation (WIP)", side="right"))
    ))
    fig_heat.update_layout(
        title={'text': "Heatmap WIP : Positions Occupées / Capacité Totale", 'x': 0.5},
        xaxis_title="Colonnes (Emplacements)",
        yaxis_title="Rangées (Étagères)",
        yaxis=dict(autorange="reversed") # Inverser l'axe Y pour faire comme une vue de haut
    )
    fig_heat = appliquer_theme_maquette(fig_heat)
    fig_heat.update_layout(height=400)
    st.plotly_chart(fig_heat, use_container_width=True)

with col_g2:
    # Graphique Stock + Cumulé (Double Axe)
    df_stock = pd.DataFrame({
        "Element": [f"élément {i}" for i in range(1, 6)],
        "Stock": [45, 70, 80, 5, 5],
        "Cumul": [20, 50, 90, 95, 100]
    })
    
    fig_mix = go.Figure()
    # Barres Primaires (Teal)
    fig_mix.add_trace(go.Bar(
        x=df_stock['Element'], y=df_stock['Stock'], 
        name="Stock", marker_color=COULEUR_PRIMAIRE, yaxis='y1'
    ))
    # Courbe Secondaire (Gris clair)
    fig_mix.add_trace(go.Scatter(
        x=df_stock['Element'], y=df_stock['Cumul'], 
        name="cummulé", mode='lines', line=dict(color=COULEUR_SECONDAIRE, width=4), yaxis='y2'
    ))

    fig_mix.update_layout(
        title={'text': "Stock", 'x': 0.5},
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        yaxis=dict(title="", range=[0, 90], showgrid=True),
        yaxis2=dict(title="", range=[0, 120], overlaying='y', side='right', ticksuffix="%", showgrid=False)
    )
    fig_mix = appliquer_theme_maquette(fig_mix)
    fig_mix.update_layout(height=400)
    st.plotly_chart(fig_mix, use_container_width=True)

# ---------------------------------------------------------
# LIGNE 3 : LES FLECHES (CHEVRONS) DU PROCESSUS
# ---------------------------------------------------------
st.markdown(f"""
    <style>
    .process-container {{
        display: flex;
        justify-content: space-between;
        background-color: {COULEUR_FOND_GRAPHIQUE};
        padding: 30px 20px;
        border-radius: 5px;
        margin-top: 20px;
        overflow: hidden;
    }}
    .chevron {{
        flex: 1;
        text-align: center;
        background-color: {COULEUR_PRIMAIRE};
        color: white;
        padding: 15px 5px 15px 25px;
        position: relative;
        margin-right: 6px;
        font-family: Arial, sans-serif;
    }}
    .chevron:last-child {{ margin-right: 0; }}
    
    /* Pointe droite de la flèche */
    .chevron::after {{
        content: "";
        position: absolute;
        right: -20px;
        top: 0;
        border-top: 34px solid transparent;
        border-bottom: 34px solid transparent;
        border-left: 20px solid {COULEUR_PRIMAIRE};
        z-index: 2;
    }}
    
    /* Creux gauche de la flèche */
    .chevron::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        border-top: 34px solid transparent;
        border-bottom: 34px solid transparent;
        border-left: 20px solid {COULEUR_FOND_GRAPHIQUE};
        z-index: 1;
    }}
    
    .chevron:first-child::before {{ display: none; }}
    .chevron:first-child {{ padding-left: 10px; border-top-left-radius: 5px; border-bottom-left-radius: 5px; }}
    .chevron:last-child::after {{ display: none; }}
    .chevron:last-child {{ border-top-right-radius: 5px; border-bottom-right-radius: 5px; padding-right: 20px; }}
    
    .chevron-titre {{ font-size: 14px; font-weight: bold; margin: 0; line-height: 1.2; }}
    .chevron-temps {{ font-size: 12px; color: {COULEUR_SECONDAIRE}; margin: 0; }}
    </style>

    <div class="process-container">
        <div class="chevron">
            <p class="chevron-titre">Réception OF</p>
            <p class="chevron-temps">5 minutes</p>
        </div>
        <div class="chevron">
            <p class="chevron-titre">Picking /appro</p>
            <p class="chevron-temps">10 minutes</p>
        </div>
        <div class="chevron">
            <p class="chevron-titre">Chargement</p>
            <p class="chevron-temps">5 minutes</p>
        </div>
        <div class="chevron">
            <p class="chevron-titre">Processus automatisé</p>
            <p class="chevron-temps">20 minutes</p>
        </div>
        <div class="chevron">
            <p class="chevron-titre">Contrôle qualité</p>
            <p class="chevron-temps">5 minutes</p>
        </div>
        <div class="chevron">
            <p class="chevron-titre">Conditionnement</p>
            <p class="chevron-temps">8 minutes</p>
        </div>
        <div class="chevron">
            <p class="chevron-titre">Stockage PF</p>
            <p class="chevron-temps">15 minutes</p>
        </div>
    </div>
""", unsafe_allow_html=True)