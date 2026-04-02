import streamlit as st
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

DROITS_ACCES = {
    "admin":          ["Performance", "Qualite", "Logistique", "Maintenance", "Donnees"],
    "manager_ops":    ["Performance", "Qualite", "Maintenance", "Donnees"],
    "manager_supply": ["Logistique", "Qualite", "Donnees"],
}

PAGE_CONFIG = {
    "Performance":  {"path": "pages/1_Performance.py",  "label": "Performances Operationnel", "color": "#3d85c8"},
    "Qualite":      {"path": "pages/2_Qualite.py",      "label": "Qualite",                   "color": "#4CAF50"},
    "Logistique":   {"path": "pages/3_Logistique.py",   "label": "Logistique / Flux",         "color": "#C0392B"},
    "Maintenance":  {"path": "pages/4_Maintenance.py",  "label": "Maintenance",               "color": "#E67E22"},
    "Donnees":      {"path": "pages/5_Donnees.py",      "label": "Donnees",                   "color": "#7B7B7B"},
}

SLIDESHOW_ORDER = ["Performance", "Qualite", "Logistique", "Maintenance", "Donnees"]

THEME_COLORS = {
    "Performance": "#3d85c8",
    "Qualite":     "#4CAF50",
    "Logistique":  "#C0392B",
    "Maintenance": "#E67E22",
    "Donnees":     "#7B7B7B",
}

_DEMO_CREDENTIALS = [
    ("admin@telefan.com",  "Admin2024!",  "admin"),
    ("ops@telefan.com",    "Ops2024!",    "manager_ops"),
    ("supply@telefan.com", "Supply2024!", "manager_supply"),
]
DEMO_USERS = {
    email: (generate_password_hash(pwd), role)
    for email, pwd, role in _DEMO_CREDENTIALS
}


def _get_db_conn():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3307")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        database="python_auth_db",
    )


def authenticate(email: str, password: str):
    try:
        conn = _get_db_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT role, password_hash FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        conn.close()
        if row and check_password_hash(row["password_hash"], password):
            return row["role"]
    except Exception:
        pass
    if email in DEMO_USERS:
        pwd_hash, role = DEMO_USERS[email]
        if check_password_hash(pwd_hash, password):
            return role
    return None


def check_auth(allowed_roles=None):
    if not st.session_state.get("logged_in"):
        st.switch_page("Home.py")
    if allowed_roles and st.session_state.get("role") not in allowed_roles:
        st.error("Acces refuse — votre profil n'a pas acces a cette page.")
        st.stop()


def render_navbar(active=""):
    role = st.session_state.get("role", "")
    pages_ok = DROITS_ACCES.get(role, [])
    sidebar_color = THEME_COLORS.get(active, "#1f4e79")

    btn_css = []
    for page in pages_ok:
        color = PAGE_CONFIG[page]["color"]
        label = PAGE_CONFIG[page]["label"]
        is_active = (page == active)
        btn_css.append(
            f'button[aria-label="{label}"] {{'
            f"background: {color} !important; color: white !important;"
            f"border-radius: 24px !important; border: none !important;"
            f"font-weight: {'bold' if is_active else '500'} !important;"
            f"font-size: 13px !important; min-height: 54px !important;"
            f"box-shadow: {'0 2px 8px rgba(0,0,0,0.25)' if is_active else '0 1px 3px rgba(0,0,0,0.15)'} !important;"
            f"outline: {'3px solid rgba(255,255,255,0.7)' if is_active else 'none'} !important;"
            f"outline-offset: -3px !important;"
            f"}}"
            f'button[aria-label="{label}"] p, button[aria-label="{label}"] span {{'
            f"color: white !important;}}"
        )

    btn_css.append(
        'button[aria-label="Deconnexion"] {'
        "background: #9E9E9E !important; color: white !important;"
        "border-radius: 24px !important; border: none !important;"
        "font-size: 13px !important; min-height: 54px !important;}"
        'button[aria-label="Deconnexion"] p, button[aria-label="Deconnexion"] span {'
        "color: white !important;}"
    )

    st.markdown(f"""<style>
    #MainMenu, footer {{visibility: hidden;}}
    [data-testid="stSidebarNav"] {{display: none !important;}}

    [data-testid="stSidebar"] {{
        background-color: {sidebar_color} !important;
    }}
    [data-testid="stSidebar"] * {{color: white !important;}}
    [data-testid="stSidebar"] hr {{border-color: rgba(255,255,255,0.35) !important;}}

    /* Champs date et texte */
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] > div > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] input {{
        background: rgba(0,0,0,0.25) !important;
        border-color: rgba(255,255,255,0.4) !important;
        color: white !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="input"] input {{color: white !important;}}

    /* Calendrier picker reste lisible en foncé */
    [data-testid="stSidebar"] [data-baseweb="calendar"] * {{color: #1a1a1a !important;}}
    [data-testid="stSidebar"] [data-baseweb="calendar"] {{background: white !important;}}

    /* Multiselect */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: rgba(0,0,0,0.25) !important;
        border-color: rgba(255,255,255,0.4) !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="tag"] {{background: rgba(255,255,255,0.25) !important;}}
    [data-testid="stSidebar"] svg {{fill: white !important;}}
    [data-testid="stSidebar"] button {{
        background: rgba(255,255,255,0.20) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
    }}
    [data-testid="stSidebar"] button:hover {{background: rgba(255,255,255,0.35) !important;}}
    {chr(10).join(btn_css)}
    </style>""", unsafe_allow_html=True)

    n = len(pages_ok)
    cols = st.columns([2] * n + [1])
    for i, page in enumerate(pages_ok):
        with cols[i]:
            if st.button(PAGE_CONFIG[page]["label"], key=f"nav_{page}", use_container_width=True):
                st.session_state["slideshow"] = False
                st.switch_page(PAGE_CONFIG[page]["path"])
    with cols[-1]:
        if st.button("Deconnexion", key="nav_logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("Home.py")

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)


def render_sidebar_filters(show_machine=True):
    """
    Filtres sidebar avec detection automatique de la plage de dates reelles.
    Retourne (start_date, end_date, resource_ids_list).
    """
    from db import get_date_range, get_resources, db_available

    # Detecte la plage une seule fois par session
    if "data_date_range" not in st.session_state:
        st.session_state["data_date_range"] = get_date_range()

    data_start, data_end = st.session_state["data_date_range"]

    st.sidebar.markdown(
        f"<div style='background:rgba(255,255,255,0.2);border-radius:8px;"
        f"padding:8px 12px;text-align:center;font-family:Arial;font-size:14px;"
        f"font-weight:bold;color:white;margin-bottom:12px;'>"
        f"{data_start.strftime('%d/%m/%Y')} — {data_end.strftime('%d/%m/%Y')}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<span style='color:white;font-weight:bold;'>Periode</span>",
                        unsafe_allow_html=True)
    start_date = st.sidebar.date_input(
        "Date debut", value=data_start, key="sidebar_start",
        min_value=data_start, max_value=data_end,
    )
    end_date = st.sidebar.date_input(
        "Date fin", value=data_end, key="sidebar_end",
        min_value=data_start, max_value=data_end,
    )

    resource_ids = []
    if show_machine:
        st.sidebar.markdown("---")
        # Charge les vrais noms de ressources
        if "resource_names" not in st.session_state:
            st.session_state["resource_names"] = get_resources()
        res_map = st.session_state["resource_names"]  # {id: name}
        options = [f"{rid} - {name}" for rid, name in sorted(res_map.items())]

        selected = st.sidebar.multiselect(
            "Ressources",
            options=options,
            default=[],
            placeholder="Toutes les ressources",
            key="sidebar_machines",
        )
        if selected:
            resource_ids = [int(s.split(" - ")[0]) for s in selected]
        else:
            resource_ids = list(res_map.keys())

    st.sidebar.markdown("<hr style='border-color:rgba(255,255,255,0.35);'/>",
                        unsafe_allow_html=True)

    # Indicateur source de donnees
    has_real_data = db_available("kpi_trs")
    status_color = "#92D050" if has_real_data else "#FFC000"
    status_text  = "Base de donnees SQL" if has_real_data else "Mode demonstration"
    st.sidebar.markdown(
        f"<div style='background:rgba(0,0,0,0.2);border-radius:6px;padding:6px 10px;"
        f"margin-bottom:8px;font-size:11px;color:white;text-align:center;'>"
        f"<span style='color:{status_color};font-weight:bold;'>●</span> {status_text}</div>",
        unsafe_allow_html=True,
    )

    # Controle diaporama
    if st.session_state.get("slideshow", False):
        st.sidebar.markdown(
            "<div style='color:white;font-size:12px;text-align:center;"
            "background:rgba(0,0,0,0.2);border-radius:6px;padding:4px;margin-bottom:6px;'>"
            "Diaporama actif</div>",
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Arreter le diaporama", use_container_width=True,
                             key="sidebar_stop_slideshow"):
            st.session_state["slideshow"] = False
            st.switch_page("Home.py")

    role_labels = {
        "admin": "Administrateur",
        "manager_ops": "Resp. Operations",
        "manager_supply": "Resp. Logistique",
    }
    role = st.session_state.get("role", "")
    st.sidebar.markdown(
        f"<div style='color:white;font-size:12px;line-height:1.6;'>"
        f"<b>{role_labels.get(role, role)}</b><br>"
        f"{st.session_state.get('email', '')}</div>",
        unsafe_allow_html=True,
    )

    return start_date, end_date, resource_ids


def handle_slideshow(current_page: str, interval_seconds: int = 15):
    if not st.session_state.get("slideshow", False):
        return False

    role = st.session_state.get("role", "")
    pages_ok = [p for p in SLIDESHOW_ORDER if p in DROITS_ACCES.get(role, [])]
    if not pages_ok:
        return False

    try:
        from streamlit_autorefresh import st_autorefresh
        count = st_autorefresh(interval=interval_seconds * 1000,
                               key=f"slideshow_{current_page}")
    except ImportError:
        count = 0

    if count > 0:
        idx = pages_ok.index(current_page) if current_page in pages_ok else 0
        next_page = pages_ok[(idx + 1) % len(pages_ok)]
        st.switch_page(PAGE_CONFIG[next_page]["path"])

    return True
