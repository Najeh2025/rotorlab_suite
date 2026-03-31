import streamlit as st

st.set_page_config(
    page_title="RotorLab Suite",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 RotorLab Suite")
st.markdown("### Plateforme d'analyse vibratoire des rotors")

st.info("Bienvenue dans RotorLab Suite! Cette application permet l'analyse et la simulation de rotors.")

# Barre latérale
with st.sidebar:
    st.header("Navigation")
    st.markdown("- Dashboard")
    st.markdown("- Pédagogique")
    st.markdown("- Simulation")
    st.markdown("- Bibliothèque")
    st.markdown("- Copilot")
# app.py
"""Point d'entrée principal de RotorLab Suite 1.0"""

#import streamlit as st

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="RotorLab Suite 1.0",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import des modules après la configuration
from core.constants import GLOBAL_CSS, init_default_material
from ui.session import init_session_state
from core.cache_manager import cache

# Initialisation
init_session_state()
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Initialisation du matériau par défaut
init_default_material()

# Vérification ROSS
try:
    import ross as rs
    ROSS_AVAILABLE = True
    ROSS_VERSION = getattr(rs, '__version__', 'unknown')
except ImportError:
    ROSS_AVAILABLE = False
    ROSS_VERSION = "non installé"

# Sidebar commune
with st.sidebar:
    st.markdown("## ⚙️ RotorLab Suite 1.0")
    st.session_state["user_name"] = st.text_input(
        "👤 Votre nom :", 
        st.session_state.get("user_name", "Utilisateur")
    )
    st.markdown("---")
    
    # Navigation
    st.radio(
        "🗺️ Navigation :",
        [
            "🏠 Tableau de Bord",
            "🎓 Mode Pédagogique",
            "🔬 Mode Simulation",
            "📚 Bibliothèque",
            "✨ SmartRotor Copilot",
            "ℹ️ À propos",
        ],
        key="nav_page"
    )
    
    # Badges
    if st.session_state.get("badges"):
        st.markdown("---")
        st.markdown("**🏅 Mes Badges :**")
        for tid, btype in st.session_state["badges"].items():
            icon = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}.get(btype, "🏅")
            st.markdown(f"{icon} {tid}")
    
    # Statut ROSS
    st.markdown("---")
    if ROSS_AVAILABLE:
        st.success(f"✅ ROSS {ROSS_VERSION}")
    else:
        st.error("❌ ROSS non installé")
        st.code("pip install ross-rotordynamics", language="bash")
    
    # Rotor actif
    rotor = cache.get("rotor", namespace="simulation")
    if rotor:
        st.markdown("---")
        st.markdown("**🔧 Rotor actif :**")
        st.caption(f"  {len(rotor.nodes)} nœuds | {rotor.m:.2f} kg")

# Navigation vers les pages
# Note: Streamlit détecte automatiquement les fichiers dans le dossier pages/
# Les pages sont déjà créées dans pages/ avec des noms comme 1_🏠_Dashboard.py
