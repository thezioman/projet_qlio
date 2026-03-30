import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. VÉRIFICATION DE SÉCURITÉ ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Accès restreint : Veuillez vous authentifier sur la page d'accueil.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(layout="wide", page_title="Maintenance T'Elefan", initial_sidebar_state="expanded")

# --- 3. CHARTE GRAPHIQUE (MAINTENANCE) ---
COULEUR_BANDEAU = "#f7a84d"

st.markdown(f"""
    <style>
    /* Fond de la page en blanc */
    .stApp, .main, .block-container {{ background-color: #ffffff !important; }}
    
    /* Masquer l'en-tête natif */
    header {{visibility: hidden !important;}}
    [data-testid="stSidebarNav"] {{display: none !important;}}
    
    /* --- LE BANDEAU TOUT EN HAUT --- */
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
    
    /* --- MENU LATÉRAL (GAUCHE) --- */
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
    
    /* COULEURS DES BOUTONS (MAINTENANCE ACTIF -> Bordure sombre) */
    /* 1. Qualité */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{ background-color: #8fc280 !important; }}
    /* 2. Performance */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{ background-color: #7ab4f5 !important; }}
    /* 3. Logistique */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {{ background-color: #c7605d !important; }}
    /* 4. Maintenance (ACTIF) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {{ background-color: #f7a84d !important; border: 2px solid #a36113 !important; }}
    /* 5. Déconnexion */
    div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {{ background-color: #cfcfcf !important; border-radius: 35px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. MENU LATÉRAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("""
    <div style="background-color: #8db4d2; padding: 15px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 30px; margin-top: -30px; color: black;">
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

# --- 5. BANDEAU DE NAVIGATION ---
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("Qualité", use_container_width=True) :
        st.switch_page("pages/Qualite.py")
with c2:
    if st.button("Performances\nOpérationnel", use_container_width=True):
        st.switch_page("pages/Performances.py")

with c3:
    if st.button("Logistique / Flux", use_container_width=True):
        st.switch_page("pages/Logistique.py")

with c4:
    st.button("Maintenance", use_container_width=True)

with c5:
    if st.button("déconnexion", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['role'] = None
        st.switch_page("login.py")


st.write("")
st.write("")

# --- 6. GRAPHIQUES ET DONNÉES ---
COULEUR_FOND_GRAPHIQUE = "#ffaa38"
COULEUR_PRIMAIRE = "#0055c7"
COULEUR_SECONDAIRE = "#9c9c9c"
COULEUR_TEXTE = "black"

def appliquer_theme_maquette(fig):
    fig.update_layout(
        paper_bgcolor=COULEUR_FOND_GRAPHIQUE,
        plot_bgcolor=COULEUR_FOND_GRAPHIQUE,
        font=dict(color=COULEUR_TEXTE),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    )
    return fig

# La maquette a deux grandes colonnes
col_gauche, col_droite = st.columns(2)

with col_gauche:
    # 1. KPI Nombre d'erreurs
    valeur_erreurs = 16
    fig_kpi = go.Figure(go.Indicator(
        mode="number",
        value=valeur_erreurs,
        title={'text': "nombre d'erreur", 'font': {'color': COULEUR_TEXTE, 'size': 18}},
        number={'font': {'color': COULEUR_TEXTE, 'size': 50}}
    ))
    fig_kpi = appliquer_theme_maquette(fig_kpi)
    fig_kpi.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_kpi, use_container_width=True)
    
    st.write("")

    # 2. Graphique Barres Horizontales (Durée)
    df_duree = pd.DataFrame({
        "Machine": ["machine 1", "machine 2", "machine 3", "machine 4", "machine 5", "machine 6", "machine 7"],
        "Durée": [150, 70, 300, 30, 75, 190, 125]
    })
    fig_duree = px.bar(df_duree, x="Durée", y="Machine", orientation='h', title="durée moyenne d'inéficacité (en minute)")
    fig_duree.update_traces(marker_color=COULEUR_PRIMAIRE, width=0.4)
    fig_duree = appliquer_theme_maquette(fig_duree)
    fig_duree.update_layout(height=350)
    st.plotly_chart(fig_duree, use_container_width=True)


with col_droite:
    # 3. Graphique Mixte (Répartitions par machine)
    df_rep_mach = pd.DataFrame({
        "Machine": ["machine 1", "machine 2", "machine 3", "machine 4", "machine 5", "machine 6", "machine 7"],
        "Erreurs": [2, 15, 28, 65, 5, 25, 12],
        "Repartition": [1, 15, 30, 48, 2, 20, 10]
    })
    
    fig_rep = go.Figure()
    # Axe Y1 : Barres bleues
    fig_rep.add_trace(go.Bar(
        x=df_rep_mach['Machine'], y=df_rep_mach['Erreurs'], 
        name="nombre d'erreur", marker_color=COULEUR_PRIMAIRE, yaxis='y1'
    ))
    # Axe Y2 : Courbe grise
    fig_rep.add_trace(go.Scatter(
        x=df_rep_mach['Machine'], y=df_rep_mach['Repartition'], 
        name="répartitions", mode='lines+markers', line=dict(color=COULEUR_SECONDAIRE, width=3), yaxis='y2'
    ))

    fig_rep.update_layout(
        title={'text': "répartitions d'erreur par machine", 'x': 0.5, 'xanchor': 'center'},
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        yaxis=dict(title="", range=[0, 70], showgrid=True),
        yaxis2=dict(title="", range=[0, 50], overlaying='y', side='right', ticksuffix="%", showgrid=False)
    )
    fig_rep = appliquer_theme_maquette(fig_rep)
    fig_rep.update_layout(height=300)
    st.plotly_chart(fig_rep, use_container_width=True)

    # 4. Graphique Barres Verticales (Répartition types d'erreur)
    df_type = pd.DataFrame({
        "Erreur": [f"erreur {i}" for i in range(1, 11)],
        "Volume": [5, 18, 24, 35, 3, 12, 10, 45, 32, 20]
    })
    fig_type = px.bar(df_type, x="Erreur", y="Volume", title="répartitions du type d'erreurs")
    fig_type.update_traces(marker_color=COULEUR_PRIMAIRE, width=0.4)
    fig_type = appliquer_theme_maquette(fig_type)
    fig_type.update_layout(height=300, yaxis_range=[0, 50])
    st.plotly_chart(fig_type, use_container_width=True)