# app.py
"""Point d'entrée principal de RotorLab Suite 1.0 - Version corrigée"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(
    page_title="RotorLab Suite 1.0",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# IMPORTS DES MODULES (après la configuration)
# =============================================================================

# Core
from core.constants import (
    MATERIALS_DB, BEARING_PRESETS, GLOBAL_CSS, TUTORIALS, init_default_material
)
from core.cache_manager import cache
from core.rotor_builder import RotorBuilder
from core.simulation_engine import SimulationEngine
from core.report_generator import ReportGenerator

# UI
from ui.components import info_card, badge, modal_table, progress_indicator
from ui.plots import (
    plot_bode_unbal, plot_campbell_with_api, plot_waterfall,
    plot_polar_unbal, plot_camp_unbal, plot_freq_resp, plot_nyquist
)

# Modules
from modules import (
    m1_constructeur, m2_statique_modal, m3_campbell,
    m4_balourd, m5_temporel_defauts, m6_rapport
)

# =============================================================================
# INITIALISATION DE LA SESSION
# =============================================================================

def init_session_state():
    """Initialise toutes les variables de session"""
    
    defaults = {
        "user_name": "Utilisateur",
        "badges": {},
        "tut_done": set(),
        "sim_count": 0,
        "chat_history": [],
        "current_page": "Tableau de Bord",  # Page courante
        "sim_module": "M1",
        "tut_active": "T1",
        
        # Tableaux pour M1
        "df_shaft": pd.DataFrame([
            {"L (m)": 0.2, "id_L (m)": 0.0, "od_L (m)": 0.05, "id_R (m)": 0.0, "od_R (m)": 0.05}
            for _ in range(5)
        ]),
        "df_disk": pd.DataFrame([
            {"nœud": 2, "Masse (kg)": 15.12, "Id (kg.m²)": 0.025, "Ip (kg.m²)": 0.047}
        ]),
        "df_bear": pd.DataFrame([
            {"nœud": 0, "Type": "Palier", "kxx": 1e6, "kyy": 1e6, "kxy": 0.0,
             "cxx": 0.0, "cyy": 0.0, "m (kg)": 0.0},
            {"nœud": 5, "Type": "Palier", "kxx": 1e6, "kyy": 1e6, "kxy": 0.0,
             "cxx": 0.0, "cyy": 0.0, "m (kg)": 0.0},
        ]),
        
        # Images pour rapport
        "img_rotor": None,
        "img_campbell_plot": None,
        
        # Résultats
        "df_modal": None,
        "df_campbell": None,
        "df_api": None,
        "api_params": None,
    }
    
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

# Vérification ROSS
try:
    import ross as rs
    ROSS_AVAILABLE = True
    ROSS_VERSION = getattr(rs, '__version__', 'unknown')
except ImportError:
    ROSS_AVAILABLE = False
    ROSS_VERSION = "non installé"

# Initialisation
init_session_state()
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
init_default_material()

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Logo et titre
    st.markdown("""
    <div style='text-align:center; margin-bottom:20px;'>
        <div style='font-size:2.5em;'>⚙️</div>
        <div style='font-size:1.2em; font-weight:bold; color:#1F5C8B;'>RotorLab Suite 1.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Profil utilisateur
    st.session_state["user_name"] = st.text_input(
        "👤 Votre nom",
        st.session_state.get("user_name", "Utilisateur")
    )
    
    st.markdown("---")
    
    # Navigation UNIQUE (sans duplication)
    st.markdown("### 🗺️ Navigation")
    
    nav_items = [
        ("🏠 Tableau de Bord", "dashboard"),
        ("🎓 Mode Pédagogique", "tutorial"),
        ("🔬 Mode Simulation", "simulation"),
        ("📚 Bibliothèque", "library"),
        ("✨ SmartRotor Copilot", "copilot"),
        ("ℹ️ À propos", "about")
    ]
    
    for label, key in nav_items:
        # Style du bouton selon la page active
        is_active = st.session_state.get("current_page") == label
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            st.session_state["current_page"] = label
            st.rerun()
    
    st.markdown("---")
    
    # Badges de progression
    badges = st.session_state.get("badges", {})
    if badges:
        st.markdown("### 🏅 Progression")
        for tid, btype in badges.items():
            icon = {"gold": "🥇", "silver": "🥈", "bronze": "🥉"}.get(btype, "🏅")
            st.markdown(f"{icon} **{tid}**")
        st.markdown("---")
    
    # Statut ROSS
    if ROSS_AVAILABLE:
        st.success(f"✅ ROSS {ROSS_VERSION}")
    else:
        st.error("❌ ROSS non installé")
        st.code("pip install ross-rotordynamics", language="bash")
    
    # Rotor actif
    rotor = cache.get("rotor", namespace="simulation")
    if rotor:
        st.markdown("---")
        st.markdown("### 🔧 Rotor actif")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nœuds", len(rotor.nodes))
        with col2:
            st.metric("Masse", f"{rotor.m:.1f} kg")
    
    st.markdown("---")
    st.caption("RotorLab Suite 1.0 • Propulsé par ROSS")

# =============================================================================
# ROUTAGE DES PAGES
# =============================================================================

# Récupération de la page courante
current_page = st.session_state.get("current_page", "Tableau de Bord")

# Affichage du contenu principal
if current_page == "🏠 Tableau de Bord":
    render_dashboard()
elif current_page == "🎓 Mode Pédagogique":
    render_tutorial_mode()
elif current_page == "🔬 Mode Simulation":
    render_simulation_mode()
elif current_page == "📚 Bibliothèque":
    render_library()
elif current_page == "✨ SmartRotor Copilot":
    render_gemini_assistant()
elif current_page == "ℹ️ À propos":
    render_about_page()

# =============================================================================
# FONCTIONS DE RENDU (à déplacer dans des fichiers séparés normalement)
# =============================================================================

def render_dashboard():
    """Page d'accueil / Tableau de bord"""
    
    user_name = st.session_state.get("user_name", "Utilisateur")
    from datetime import datetime
    hour = datetime.now().hour
    
    if hour < 12:
        greeting = "Bonjour"
    elif hour < 18:
        greeting = "Bon après-midi"
    else:
        greeting = "Bonsoir"
    
    st.markdown(f"""
    <div style='text-align:center; padding:10px 0 15px'>
        <h1 style='color:#1F5C8B; font-size:2.8em; margin:0; font-weight:700;'>
            ⚙️ RotorLab Suite 1.0
        </h1>
        <p style='color:#666; font-size:1.1em; margin:5px 0 0'>
            Plateforme d'Ingénierie Avancée pour la Dynamique des Rotors
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Message de bienvenue
    st.markdown(f"""
    <div style='background:linear-gradient(135deg, #1F5C8B08, #FFFFFF); 
                border-radius:12px; padding:12px 20px; margin-bottom:25px;
                border-left:4px solid #1F5C8B;'>
        <div style='font-size:1.05em;'>{greeting}, <b>{user_name}</b> ! 👋</div>
        <div style='color:#666; font-size:0.9em; margin-top:4px;'>
            Prêt à analyser votre rotor ? Sélectionnez un module ci-dessous.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Accès rapide aux modules
    st.markdown("### 🚀 Accès Rapide aux Modules")
    
    modules = [
        ("M1", "🏗️ Constructeur", "Géométrie, Matériaux, Paliers"),
        ("M2", "📊 Statique & Modal", "Déflexion, Fréquences propres"),
        ("M3", "📈 Campbell", "Stabilité, Vitesses critiques, API"),
        ("M4", "🌀 Balourd & H(jω)", "Bode, Nyquist, Norme ISO 1940"),
        ("M5", "⏱️ Temporel", "Défauts, Cascade 3D"),
        ("M6", "📄 Rapport & Export", "PDF, Excel, HTML"),
    ]
    
    cols = st.columns(3)
    for i, (m_id, title, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div style='background:#FFFFFF; border:1px solid #E8E8E8; border-radius:12px; 
                        padding:14px 12px; margin-bottom:12px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                    <span style='background:#1F5C8B20; color:#1F5C8B; padding:4px 10px; 
                                 border-radius:20px; font-size:12px; font-weight:bold;'>
                        {m_id}
                    </span>
                </div>
                <div style='font-weight:600; font-size:1em; margin:8px 0 4px;'>{title}</div>
                <div style='font-size:0.75em; color:#888;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"⚙️ Lancer {m_id}", key=f"btn_dash_{m_id}", 
                         use_container_width=True):
                st.session_state["current_page"] = "🔬 Mode Simulation"
                st.session_state["sim_module"] = m_id
                st.rerun()
    
    st.markdown("---")
    
    # Tutoriels rapides
    st.markdown("### 🎓 Tutoriels Rapides")
    
    tut_done = st.session_state.get("tut_done", set())
    level_colors = {
        "🟢 Débutant": "#22863A",
        "🔵 Intermédiaire": "#1F5C8B",
        "🔴 Avancé": "#C55A11"
    }
    
    tcols = st.columns(4)
    for i, (tid, tdata) in enumerate(TUTORIALS.items()):
        done = tid in tut_done
        color = level_colors.get(tdata['level'], "#1F5C8B")
        
        with tcols[i]:
            st.markdown(f"""
            <div style='background:{"#F0FFF4" if done else "#FFFFFF"}; 
                        border:1px solid {color}30; border-radius:12px; padding:12px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                    <span style='background:{color}; color:white; padding:2px 8px; 
                                 border-radius:20px; font-size:10px;'>
                        {tdata['level']}
                    </span>
                    <span>{'✅' if done else '📘'}</span>
                </div>
                <div style='font-weight:500; font-size:0.85em;'>{tdata['title'][:35]}</div>
                <div style='font-size:10px; color:#888; margin:6px 0;'>⏱ {tdata['duration']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📖 Démarrer", key=f"btn_tut_{tid}", use_container_width=True):
                st.session_state["current_page"] = "🎓 Mode Pédagogique"
                st.session_state["tut_active"] = tid
                st.rerun()
    
    st.markdown("---")
    
    # Cas d'étude
    st.markdown("### 🏭 Cas d'Étude Industriel")
    
    if ROSS_AVAILABLE and st.button("🔌 Charger Compresseur Centrifuge", use_container_width=True, type="primary"):
        with st.spinner("Chargement du modèle industriel..."):
            try:
                import ross as rs
                comp = rs.compressor_example()
                cache.set("rotor", comp, namespace="simulation")
                
                # Synchronisation des tableaux
                shaft_data = []
                for el in comp.shaft_elements:
                    shaft_data.append({
                        "L (m)": el.L,
                        "id_L (m)": el.idl,
                        "od_L (m)": el.odl,
                        "id_R (m)": el.idr,
                        "od_R (m)": el.odr
                    })
                st.session_state.df_shaft = pd.DataFrame(shaft_data)
                
                disk_data = []
                for disk in comp.disk_elements:
                    disk_data.append({
                        "nœud": disk.n,
                        "Masse (kg)": disk.m,
                        "Id (kg.m²)": disk.Id,
                        "Ip (kg.m²)": disk.Ip
                    })
                st.session_state.df_disk = pd.DataFrame(disk_data)
                
                bearing_data = []
                for brg in comp.bearing_elements:
                    bearing_data.append({
                        "nœud": brg.n,
                        "Type": "Palier",
                        "kxx": brg.kxx[0] if hasattr(brg.kxx, '__iter__') else brg.kxx,
                        "kyy": brg.kyy[0] if hasattr(brg.kyy, '__iter__') else brg.kyy,
                        "kxy": brg.kxy[0] if hasattr(brg.kxy, '__iter__') else brg.kxy,
                        "cxx": brg.cxx[0] if hasattr(brg.cxx, '__iter__') else brg.cxx,
                        "cyy": brg.cyy[0] if hasattr(brg.cyy, '__iter__') else brg.cyy,
                        "m (kg)": 0.0
                    })
                st.session_state.df_bear = pd.DataFrame(bearing_data)
                
                st.success("✅ Compresseur chargé avec succès !")
                st.balloons()
            except Exception as e:
                st.error(f"Erreur : {e}")

def render_tutorial_mode():
    """Mode Pédagogique"""
    st.title("🎓 Mode Pédagogique — Tutoriels ROSS Officiels")
    
    tut_id = st.session_state.get("tut_active", "T1")
    
    if tut_id not in TUTORIALS:
        tut_id = "T1"
    
    tut = TUTORIALS[tut_id]
    
    # Sélecteur de tutoriel
    tut_keys = list(TUTORIALS.keys())
    selected = st.selectbox(
        "Sélectionnez un tutoriel :",
        tut_keys,
        index=tut_keys.index(tut_id),
        format_func=lambda x: f"{TUTORIALS[x]['level']} — {TUTORIALS[x]['title'][:50]}"
    )
    
    if selected != tut_id:
        st.session_state["tut_active"] = selected
        st.rerun()
    
    # En-tête
    api_badges = "".join(f"<span class='mod-badge'>{a}</span>" for a in tut["api"])
    st.markdown(f"""
    <div class='card'>
        <h2 style='color:#1F5C8B; margin:0'>{tut['title']}</h2>
        <p>{tut['level']} &nbsp;|&nbsp; ⏱ {tut['duration']}</p>
        <p><b>API ROSS utilisée :</b> {api_badges}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation des étapes
    steps = tut["steps"]
    n_steps = len(steps)
    step_key = f"tut_step_{tut_id}"
    current_step = st.session_state.get(step_key, 0)
    
    # Barre de progression
    st.progress((current_step + 1) / n_steps)
    
    # Sélection d'étape dans la sidebar (ou en haut)
    step_idx = st.radio(
        "Étapes :",
        range(n_steps),
        index=min(current_step, n_steps - 1),
        format_func=lambda i: f"{'✅' if i < current_step else '▶️' if i == current_step else '⬜'} Étape {i+1}: {steps[i]['title']}",
        horizontal=True
    )
    
    step = steps[step_idx]
    st.markdown(f"## Étape {step_idx+1} — {step['title']}")
    
    # Onglets
    tab_th, tab_sim, tab_code = st.tabs(["📖 Théorie", "🔬 Simulation", "💻 Code"])
    
    with tab_th:
        st.info(step["theory"])
        st.markdown(f"**🎯 Objectif :** {step['objective']}")
    
    with tab_code:
        st.markdown("**Code de référence ROSS :**")
        st.code(step["code"], language="python")
        st.download_button(
            "⬇️ Télécharger ce snippet",
            data=step["code"].encode(),
            file_name=f"ross_{step['id']}.py",
            mime="text/plain"
        )
    
    with tab_sim:
        st.info("💡 Simulation interactive disponible dans la version complète.")
        st.markdown(f"Exécutez le code ci-dessus dans votre environnement Python pour voir les résultats.")
    
    # Navigation
    col_prev, col_next = st.columns(2)
    with col_prev:
        if step_idx > 0:
            if st.button("⬅️ Précédent", use_container_width=True):
                st.session_state[step_key] = step_idx - 1
                st.rerun()
    with col_next:
        if step_idx < n_steps - 1:
            if st.button("Suivant ➡️", type="primary", use_container_width=True):
                st.session_state[step_key] = step_idx + 1
                st.rerun()
    
    # Validation
    if step_idx == n_steps - 1:
        if st.button("🏆 Terminer ce tutoriel", type="primary", use_container_width=True):
            tut_done = st.session_state.get("tut_done", set())
            tut_done.add(tut_id)
            st.session_state["tut_done"] = tut_done
            badges = st.session_state.get("badges", {})
            badges[tut_id] = "gold"
            st.session_state["badges"] = badges
            st.balloons()
            st.success(f"🥇 Tutoriel {tut['title'][:30]} complété !")

def render_simulation_mode():
    """Mode Simulation"""
    st.title("🔬 Mode Simulation")
    
    module_options = [
        "M1 🏗️ Constructeur",
        "M2 📊 Statique & Modal",
        "M3 📈 Campbell & Stabilité",
        "M4 🌀 Balourd",
        "M5 ⏱️ Temporel",
        "M6 📄 Rapport PDF"
    ]
    
    sim_module = st.session_state.get("sim_module", "M1")
    default_idx = 0
    for i, opt in enumerate(module_options):
        if sim_module in opt:
            default_idx = i
            break
    
    selected_mod = st.radio(
        "Module :",
        module_options,
        index=default_idx,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.session_state["sim_module"] = selected_mod[:2]
    st.markdown("---")
    
    # Routage vers les modules
    if "M1" in selected_mod:
        m1_constructeur.render()
    elif "M2" in selected_mod:
        m2_statique_modal.render()
    elif "M3" in selected_mod:
        m3_campbell.render()
    elif "M4" in selected_mod:
        m4_balourd.render()
    elif "M5" in selected_mod:
        m5_temporel_defauts.render()
    elif "M6" in selected_mod:
        m6_rapport.render()

def render_library():
    """Bibliothèque"""
    st.title("📚 Bibliothèque — Documentation ROSS")
    
    tab_ex, tab_theory, tab_api = st.tabs(["🏭 Exemples", "📐 Théorie", "🛠️ API ROSS"])
    
    with tab_ex:
        st.markdown("### Exemples officiels")
        if ROSS_AVAILABLE and st.button("Charger compresseur centrifuge"):
            try:
                import ross as rs
                comp = rs.compressor_example()
                cache.set("rotor", comp, namespace="simulation")
                st.success("Compresseur chargé !")
            except Exception as e:
                st.error(f"Erreur : {e}")
    
    with tab_theory:
        st.markdown("""
        ## Fondements Théoriques
        
        ### Équation du mouvement
        """)
        st.latex(r"[M]\{\ddot{q}\} + ([C]+[G])\{\dot{q}\} + [K]\{q\} = \{F(t)\}")
        
    with tab_api:
        st.markdown("""
        ## API ROSS
        
        | Méthode | Description |
        |---------|-------------|
        | `run_modal()` | Analyse modale |
        | `run_campbell()` | Diagramme de Campbell |
        | `run_unbalance_response()` | Réponse au balourd |
        """)

def render_gemini_assistant():
    """Assistant IA"""
    st.title("✨ SmartRotor Copilot")
    st.info("Assistant IA spécialisé en dynamique des rotors. (Configuration API requise)")

def render_about_page():
    """À propos"""
    st.title("ℹ️ À propos")
    st.markdown("""
    **RotorLab Suite 1.0** est une plateforme avancée de modélisation et de simulation 
    dédiée à la dynamique des rotors.
    
    Développée par **Pr. Najeh Ben Guedria**.
    
    Basée sur la bibliothèque open-source **ROSS** (Rotordynamic Open-Source Software).
    """)

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Le routage est déjà fait plus haut
    pass
