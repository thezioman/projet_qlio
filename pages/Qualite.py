import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. VÉRIFICATION DE SÉCURITÉ ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Accès restreint : Veuillez vous authentifier sur la page d'accueil.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Qualité T'Elefan", initial_sidebar_state="expanded")

# --- 3. CHARTE GRAPHIQUE QUALITÉ (VERT) ---
COULEUR_VERT_PRINCIPAL = "#5E8E47" # Vert forêt de la maquette

st.markdown(f"""
    <style>
    /* Fond de la page en blanc */
    .stApp, .main, .block-container {{ background-color: #ffffff !important; }}
    
    /* Masquer l'en-tête natif */
    header {{visibility: hidden !important;}}
    [data-testid="stSidebarNav"] {{display: none !important;}}
    
    /* --- LE BANDEAU VERT TOUT EN HAUT --- */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 120px; 
        background-color: {COULEUR_VERT_PRINCIPAL} !important; 
        z-index: 0;
    }}
    
    .block-container {{
        padding-top: 1.5rem !important; 
        position: relative;
        z-index: 1;
    }}
    
    /* --- MENU LATÉRAL (GAUCHE) --- */
    [data-testid="stSidebar"] {{
        background-color: {COULEUR_VERT_PRINCIPAL} !important; 
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

    /* --- BOUTONS DE NAVIGATION (HAUT) --- */
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
    
    /* COULEURS DES BOUTONS */
    /* 1. Qualité (ACTIF -> Bordure sombre) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{ background-color: #8fc280 !important; border: 2px solid #28541a !important; }}
    /* 2. Performance (Bleu sans bordure) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{ background-color: #7ab4f5 !important; }}
    /* 3. Logistique */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {{ background-color: #c7605d !important; }}
    /* 4. Maintenance */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {{ background-color: #d4ae65 !important; }}
    /* 5. Déconnexion */
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {{ background-color: #cfcfcf !important; border-radius: 35px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("""
    <div style="background-color: #8fc280; padding: 15px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 30px; margin-top: -30px; color: black;">
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
    # On est sur Qualité, donc le bouton ne fait rien
    st.button("Qualité", use_container_width=True) 

with c2:
    if st.button("Performances\nOpérationnel", use_container_width=True):
        # Si le fichier s'appelle "Performance.py" (sans S), enlève le S ici !
        st.switch_page("pages/Performances.py")

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

# --- 6. GRAPHIQUES ET DONNÉES ---
COULEUR_TEXTE = "white"
COULEUR_BARRES_VIOLET = "#A768B4" 
COULEUR_BARRES_GRIS = "#555555"   

def appliquer_theme_maquette(fig):
    fig.update_layout(
        paper_bgcolor=COULEUR_VERT_PRINCIPAL,
        plot_bgcolor=COULEUR_VERT_PRINCIPAL,
        font=dict(color=COULEUR_TEXTE),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', zeroline=False)
    )
    return fig


col_g1, col_g2 = st.columns(2)

# G1 : TRS
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
    fig_trs.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_trs, use_container_width=True)

# G2 : MTBF / MTTR (Barres groupées)
with col_g2:
    df_mtbf = pd.DataFrame({
        "Machine": ["Machine 1", "Machine 2", "Machine 3", "Machine 4", "Machine 5"],
        "Série1": [30, 25, 50, 40, 15],
        "Série2": [5, 4, 3, 8, 6]
    })
    
    fig_mtbf = go.Figure()
    fig_mtbf.add_trace(go.Bar(x=df_mtbf['Machine'], y=df_mtbf['Série1'], name='Série1', marker_color=COULEUR_BARRES_VIOLET))
    fig_mtbf.add_trace(go.Bar(x=df_mtbf['Machine'], y=df_mtbf['Série2'], name='Série2', marker_color=COULEUR_BARRES_GRIS))
    
    fig_mtbf.update_layout(
        barmode='group',
        title={'text': "MTBF MTTR en heure", 'x': 0.5, 'xanchor': 'center'},
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    fig_mtbf = appliquer_theme_maquette(fig_mtbf)
    fig_mtbf.update_layout(height=350, yaxis_range=[0, 60])
    st.plotly_chart(fig_mtbf, use_container_width=True)

# --- LIGNE 2 (Pleine largeur) : RÉPARTITIONS PAR ERREUR (Double Axe) ---
df_erreurs = pd.DataFrame({
    "Erreur": [f"erreur {i}" for i in range(1, 11)],
    "Volume": [20, 45, 85, 12, 35, 12, 48, 46, 34, 15], # Barres violettes
    "Tendance": [5, 15, 30, 5, 20, 10, 35, 55, 75, 100] # Courbe grise (%)
})

fig_err = go.Figure()

# Ajout des barres (axe Y1 à gauche)
fig_err.add_trace(go.Bar(
    x=df_erreurs['Erreur'], y=df_erreurs['Volume'], 
    marker_color=COULEUR_BARRES_VIOLET, name="Volume",
    yaxis='y1'
))

# Ajout de la courbe (axe Y2 à droite)
fig_err.add_trace(go.Scatter(
    x=df_erreurs['Erreur'], y=df_erreurs['Tendance'], 
    mode='lines', line=dict(color=COULEUR_BARRES_GRIS, width=4), name="Tendance",
    yaxis='y2'
))

fig_err.update_layout(
    title={'text': "répartitions par erreur", 'x': 0.5, 'xanchor': 'center'},
    showlegend=False,
    yaxis=dict(
        title="",
        range=[0, 90],
        showgrid=True, gridcolor='rgba(255,255,255,0.2)'
    ),
    # Configuration du 2ème axe à droite
    yaxis2=dict(
        title="",
        range=[0, 120],
        overlaying='y',
        side='right',
        ticksuffix="%",
        showgrid=False # On cache la grille du 2ème axe pour éviter un quadrillage illisible
    )
)
fig_err = appliquer_theme_maquette(fig_err)
fig_err.update_layout(height=400)
st.plotly_chart(fig_err, use_container_width=True)