import streamlit as st
import os, sys, subprocess, tempfile
from auth import authenticate, DROITS_ACCES, PAGE_CONFIG, THEME_COLORS

st.set_page_config(
    page_title="T'Elefan – Connexion",
    page_icon="🏭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
section[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
.stApp {background-color: #ffffff;}

/* Texte global en foncé */
.stApp, .stApp p, .stApp span, .stApp label,
.stApp h1, .stApp h2, .stApp h3,
.stMarkdown, .stMarkdown p,
[data-testid="stText"] {color: #1a1a1a !important;}

div[data-baseweb="input"] > div {
    border-radius: 6px !important;
    border: 1.5px solid #ccc !important;
    background: #f7f7f7 !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="input"] input::placeholder {
    color: #1a1a1a !important;
}
input, input::placeholder {
    color: #1a1a1a !important;
}
div[data-testid="stFormSubmitButton"] button {
    background: #1a1a1a !important;
    color: white !important;
    border-radius: 6px !important;
    font-size: 15px !important;
    height: 44px !important;
    border: none !important;
    width: 100%;
}
div[data-testid="stFormSubmitButton"] button p,
div[data-testid="stFormSubmitButton"] button span {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session ──────────────────────────────────────────────────────────────────
for key, default in [("logged_in", False), ("role", None), ("email", None),
                     ("slideshow", False), ("slideshow_interval", 15)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# PAGE DE CONNEXION
# ============================================================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='font-family:Georgia,serif;font-size:42px;font-weight:bold;"
        "text-align:center;color:#1a1a1a;margin-bottom:4px;'>T'Elefan</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;font-family:Georgia,serif;font-size:18px;"
        "color:#333;margin-bottom:32px;'>Gestion ligne FESTO</p>",
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            "<p style='font-family:Arial;font-size:16px;font-weight:bold;"
            "text-align:center;color:#222;margin-bottom:16px;'>connexion</p>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            email    = st.text_input("", placeholder="identifiant", label_visibility="collapsed")
            password = st.text_input("", type="password", placeholder="mot de passe",
                                     label_visibility="collapsed")
            submitted = st.form_submit_button("connexion", use_container_width=True)

        if submitted:
            role = authenticate(email, password)
            if role:
                st.session_state.logged_in = True
                st.session_state.role      = role
                st.session_state.email     = email
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;font-family:Arial;font-size:12px;"
        "color:#aaa;'>IUT Lumière Lyon 2 — SAE MES 4.0</p>",
        unsafe_allow_html=True,
    )

# ============================================================================
# ACCUEIL APRÈS CONNEXION
# ============================================================================
else:
    role     = st.session_state.role
    pages_ok = DROITS_ACCES.get(role, [])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='font-family:Georgia,serif;font-size:38px;font-weight:bold;"
        "text-align:center;color:#1a1a1a;margin-bottom:4px;'>T'Elefan</h1>",
        unsafe_allow_html=True,
    )

    role_labels = {
        "admin":          "Administrateur",
        "manager_ops":    "Responsable Opérations",
        "manager_supply": "Responsable Logistique",
    }
    st.markdown(
        f"<p style='text-align:center;font-family:Arial;font-size:14px;color:#555;"
        f"margin-bottom:24px;'>Bienvenue sur le tableau de bord pour la gestion de la ligne<br>"
        f"Festo pour T'Elefan. Voici vos rapports qui sont disponibles&nbsp;:<br>"
        f"<small style='color:#999;'>Connecté en tant que : {role_labels.get(role, role)}</small></p>",
        unsafe_allow_html=True,
    )

    # ── Statut données ─────────────────────────────────────────────────────
    from db import db_available, get_date_range
    has_real = db_available("kpi_trs")
    if has_real:
        d_start, d_end = get_date_range()
        st.markdown(
            f"<div style='text-align:center;background:#DFFFD8;border-radius:8px;"
            f"padding:8px 16px;margin-bottom:20px;font-family:Arial;font-size:13px;color:#375623;'>"
            f"<b>● Base de données chargée</b> — du {d_start.strftime('%d/%m/%Y')} au {d_end.strftime('%d/%m/%Y')}"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='text-align:center;background:#FFF3CC;border-radius:8px;"
            "padding:8px 16px;margin-bottom:20px;font-family:Arial;font-size:13px;color:#7B4000;'>"
            "<b>● Mode démonstration</b> — données simulées (SQL FESTO non trouvé)"
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Boutons de navigation ──────────────────────────────────────────────
    PAGE_COLORS = {
        "Performance": "#3d85c8",
        "Qualite":     "#4CAF50",
        "Logistique":  "#C0392B",
        "Maintenance": "#E67E22",
        "Donnees":     "#7B7B7B",
    }
    DESC_MAP = {
        "Performance": "Performances Operationnel",
        "Qualite":     "Qualite",
        "Logistique":  "Logistique / Flux",
        "Maintenance": "Maintenance",
        "Donnees":     "Donnees",
    }

    # Ciblage par aria-label (Streamlit met le label du bouton comme aria-label)
    btn_styles = ""
    for page in pages_ok:
        color = PAGE_COLORS.get(page, "#555")
        label = DESC_MAP.get(page, page)
        btn_styles += (
            f'button[aria-label="{label}"] {{'
            f'background: {color} !important;'
            f'color: white !important; border-radius: 30px !important;'
            f'height: 52px !important; font-size: 16px !important;'
            f'font-weight: bold !important; border: none !important;}}'
            f'button[aria-label="{label}"] p,'
            f'button[aria-label="{label}"] span {{'
            f'color: white !important;}}'
        )
    st.markdown(f"<style>{btn_styles}</style>", unsafe_allow_html=True)

    _, col_btns, _ = st.columns([1, 2, 1])
    with col_btns:
        for page in pages_ok:
            if st.button(DESC_MAP.get(page, page), key=f"home_{page}", use_container_width=True):
                st.session_state["slideshow"] = False
                st.switch_page(PAGE_CONFIG[page]["path"])

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Boutons action ─────────────────────────────────────────────────
        st.markdown("""<style>
        div[data-testid='stVerticalBlock'] button[kind='secondary'] {
            background: #C8C8C8 !important;
            color: #333 !important;
            border-radius: 30px !important;
            height: 48px !important;
            font-size: 14px !important;
            border: none !important;
        }
        </style>""", unsafe_allow_html=True)

        # Mode diaporama
        st.markdown("---")

        interval = st.select_slider(
            "Durée par page (secondes)",
            options=[5, 10, 15, 20, 30, 60],
            value=st.session_state.get("slideshow_interval", 15),
            key="interval_slider",
        )
        st.session_state["slideshow_interval"] = interval

        slideshow_on = st.session_state.get("slideshow", False)
        col_dia, col_stop = st.columns(2)
        with col_dia:
            if st.button(
                "▶ Mode diaporama" if not slideshow_on else "▶ Diaporama actif",
                key="btn_slideshow",
                use_container_width=True,
                disabled=slideshow_on,
            ):
                st.session_state["slideshow"] = True
                # Démarre sur la première page accessible
                first = pages_ok[0] if pages_ok else "Performance"
                st.switch_page(PAGE_CONFIG[first]["path"])

        with col_stop:
            if st.button("⏹ Arrêter", key="btn_stop", use_container_width=True,
                         disabled=not slideshow_on):
                st.session_state["slideshow"] = False
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Visualiser les données", key="home_donnees_btn", use_container_width=True):
            if "Donnees" in pages_ok:
                st.switch_page(PAGE_CONFIG["Donnees"]["path"])

        if st.button("déconnexion", key="home_logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # ── Import SQL (admin uniquement) ──────────────────────────────────────────
    if role == "admin":
        st.markdown("<br>", unsafe_allow_html=True)
        _, col_imp, _ = st.columns([1, 2, 1])
        with col_imp:
            with st.expander("Importer un nouveau jeu de données SQL"):
                st.markdown(
                    "<p style='font-size:13px;color:#555;margin-bottom:8px;'>"
                    "Chargez un fichier <b>.sql</b> exporté depuis le MES FESTO. "
                    "Les données actuelles seront remplacées et tous les KPIs recalculés.</p>",
                    unsafe_allow_html=True,
                )
                uploaded = st.file_uploader(
                    "Fichier SQL FESTO", type=["sql"], label_visibility="collapsed"
                )
                if uploaded is not None:
                    if st.button("Lancer l'import", key="btn_import_sql", use_container_width=True):
                        app_dir = os.path.dirname(os.path.abspath(__file__))
                        tmp_path = os.path.join(app_dir, "_upload_tmp.sql")
                        try:
                            with open(tmp_path, "wb") as f:
                                f.write(uploaded.getvalue())

                            with st.spinner("Ingestion des données en cours..."):
                                r1 = subprocess.run(
                                    [sys.executable, os.path.join(app_dir, "pipeline_01_ingestion.py"), tmp_path],
                                    capture_output=True, text=True, timeout=300,
                                )

                            if r1.returncode != 0:
                                st.error("Erreur lors de l'ingestion.")
                                st.code(r1.stderr or r1.stdout)
                            else:
                                with st.spinner("Calcul des KPIs..."):
                                    r2 = subprocess.run(
                                        [sys.executable, os.path.join(app_dir, "pipeline_02_eclatement_kpis.py")],
                                        capture_output=True, text=True, timeout=600,
                                    )

                                if r2.returncode != 0:
                                    st.error("Erreur lors du calcul des KPIs.")
                                    st.code(r2.stderr or r2.stdout)
                                else:
                                    # Invalide le cache de session
                                    for k in ["data_date_range", "resource_names"]:
                                        st.session_state.pop(k, None)
                                    st.success(
                                        f"Import reussi — fichier : {uploaded.name}. "
                                        "Les tableaux de bord affichent maintenant le nouveau jeu de données."
                                    )
                        except subprocess.TimeoutExpired:
                            st.error("Timeout : l'import a pris trop de temps (> 10 min).")
                        except Exception as e:
                            st.error(f"Erreur inattendue : {e}")
                        finally:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;font-family:Arial;font-size:12px;color:#aaa;'>"
        "IUT Lumière Lyon 2 — SAE MES 4.0 — Ligne FESTO</p>",
        unsafe_allow_html=True,
    )
