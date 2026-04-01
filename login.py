import streamlit as st

st.set_page_config(page_title="T'Elefan - Accueil", layout="centered")

# Définition des profils et accès
DROITS_ACCES = {
    "admin": ["Performance", "Qualite", "Logistique", "Maintenance"],
    "manager_ops": ["Performance", "Qualite", "Maintenance"], 
    "manager_supply": ["Logistique", "Qualite"]              
}

#  CSS 
st.markdown("""
    <style>
    .stApp {background-color: #FFFFFF;}
    #MainMenu, footer, header {visibility: hidden;}

    .titre-principal {font-family: Arial; font-size: 50px; font-weight: bold; text-align: center; color: black; margin-top: 10px;}
    .texte-bienvenue {font-family: Arial; font-size: 18px; text-align: center; color: #333; margin-bottom: 30px;}

    /* Champs de saisie du login */
    div[data-baseweb="input"] {background-color: #b1b2b5 !important; border-radius: 2px; border: none;}
    input[class] {color: #888282 !important; font-weight: bold;}
    
    div[data-testid="stFormSubmitButton"] button {background-color: #b1b2b5; color: black; border: none; font-weight: bold; width: 100%;}

    /* Configuration globale des boutons du tableau de bord */
    div.stButton > button {
        height: 110px;
        width: 100%;
        border-radius: 10px;
        border: none;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 15px;
        background-color: #f8f9fa; /* Couleur par défaut (gris clair) */
        color: black !important;
    }
    
    /* Autoriser les sauts de ligne dans le texte du bouton */
    div.stButton > button p {
        white-space: pre-wrap; 
        font-size: 18px;
        font-weight: bold;
    }
    
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* --- APPLICATION DES COULEURS VIA LES MARQUEURS INVISIBLES --- */
    
    /* Bouton Bleu (Performance) */
    div[data-testid="stElementContainer"]:has(.marker-perf) + div[data-testid="stElementContainer"] button {
        background-color: #4da6ff !important;
        color: white !important;
        border: 2px solid #004080 !important;
    }

    /* Bouton Vert (Qualité) */
    div[data-testid="stElementContainer"]:has(.marker-qual) + div[data-testid="stElementContainer"] button {
        background-color: #2eb82e !important;
        color: white !important;
        border: 2px solid #006600 !important;
    }

    /* Bouton Rouge (Logistique) */
    div[data-testid="stElementContainer"]:has(.marker-logi) + div[data-testid="stElementContainer"] button {
        background-color: #ff4d4d !important;
        color: white !important;
        border: 2px solid #990000 !important;
    }

    /* Bouton Orange (Maintenance) */
    div[data-testid="stElementContainer"]:has(.marker-main) + div[data-testid="stElementContainer"] button {
        background-color: #ff9933 !important;
        color: white !important;
        border: 2px solid #cc6600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Variables de session
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None

# MODULE D'AUTHENTIFICATION
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="titre-principal">T’Elefan</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; margin-bottom:20px;">Connexion sécurisée</div>', unsafe_allow_html=True)
        
        with st.form("login"):
            email = st.text_input("Identifiant", placeholder="identifiant", label_visibility="collapsed")
            st.write("") 
            password = st.text_input("Mot de passe", type="password", placeholder="mot de passe", label_visibility="collapsed")
            st.write("") 
            
            if st.form_submit_button("connexion", use_container_width=True):
                role_trouve = None
                
                # Vérification statique des identifiants
                if email == "admin@telefan.com" and password == "admin123":
                    role_trouve = "admin"
                elif email == "ops@telefan.com" and password == "ops123":
                    role_trouve = "manager_ops"
                elif email == "supply@telefan.com" and password == "supply123":
                    role_trouve = "manager_supply"
                
                if role_trouve:
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = role_trouve
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect")

# MODULE DE NAVIGATION
else:
    user_role = st.session_state['role']
    pages_autorisees = DROITS_ACCES.get(user_role, [])

    st.markdown('<div class="titre-principal">T’Elefan</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="texte-bienvenue">
    Bienvenue sur le tableau de bord pour la gestion de la ligne Festo pour T'Elefan.<br>
    Voici vos rapports qui sont disponibles :
    </div>
    """, unsafe_allow_html=True)
    
    # Première rangée de boutons
    c1, c2 = st.columns(2)
    with c1:
        if "Performance" in pages_autorisees:
            
            st.markdown('<div class="marker-perf"></div>', unsafe_allow_html=True)
            if st.button("PERFORMANCE\n\nTRS, Disponibilité, Cadence", use_container_width=True):
                st.switch_page("pages/Performances.py")

    with c2:
        if "Qualite" in pages_autorisees:
            st.markdown('<div class="marker-qual"></div>', unsafe_allow_html=True)
            if st.button("QUALITÉ\n\nRebuts, Fiabilité, Pannes", use_container_width=True):
                st.switch_page("pages/Qualite.py")

    # Deuxième rangée de boutons
    c3, c4 = st.columns(2)
    with c3:
        if "Logistique" in pages_autorisees:
            st.markdown('<div class="marker-logi"></div>', unsafe_allow_html=True)
            if st.button("LOGISTIQUE\n\nStocks, Délais, OTD", use_container_width=True):
                st.switch_page("pages/Logistique.py")

    with c4:
        if "Maintenance" in pages_autorisees:
            st.markdown('<div class="marker-main"></div>', unsafe_allow_html=True)
            if st.button("MAINTENANCE\n\nPlanification, Alertes", use_container_width=True):
                st.switch_page("pages/Maintenance.py")

    # Gestion de la déconnexion
    st.write("---")
    col_vide1, col_btn, col_vide2 = st.columns([1, 1, 1])
    with col_btn:
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['role'] = None
            st.rerun()