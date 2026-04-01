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
# VÉRIFICATION ROSS
# =============================================================================

try:
    import ross as rs
    ROSS_AVAILABLE = True
    ROSS_VERSION = getattr(rs, '__version__', 'unknown')
except ImportError:
    ROSS_AVAILABLE = False
    ROSS_VERSION = "non installé"

# =============================================================================
# CONSTANTES (simplifiées pour la correction)
# =============================================================================

MATERIALS_DB = {
    "Acier standard (AISI 1045)": {"rho": 7810.0, "E": 211e9, "G_s": 81.2e9},
    "Acier inoxydable (316L)": {"rho": 7990.0, "E": 193e9, "G_s": 74.0e9},
    "Aluminium (7075-T6)": {"rho": 2810.0, "E": 72e9, "G_s": 27.0e9},
}

BEARING_PRESETS = {
    "Roulement à billes": {"kxx": 1e7, "kyy": 1e7, "kxy": 0.0, "cxx": 500.0, "cyy": 500.0},
    "Palier rigide": {"kxx": 1e9, "kyy": 1e9, "kxy": 0.0, "cxx": 100.0, "cyy": 100.0},
}

TUTORIALS = {
    "T1": {
        "title": "Part 1 — Création du Modèle",
        "level": "🟢 Débutant",
        "duration": "~15 min",
        "api": ["Material", "ShaftElement", "DiskElement", "BearingElement", "Rotor"],
        "steps": [
            {"id": "T1_S1", "title": "Définir un matériau",
             "theory": "Le matériau définit les propriétés physiques de l'arbre.",
             "objective": "Créer un matériau Acier",
             "code": "import ross as rs\nsteel = rs.Material(name='Steel', rho=7810, E=211e9, G_s=81.2e9)"},
            {"id": "T1_S2", "title": "Créer les éléments d'arbre",
             "theory": "L'arbre est discrétisé en éléments de poutre de Timoshenko.",
             "objective": "Créer 5 éléments d'arbre",
             "code": "shaft = [rs.ShaftElement(L=0.25, idl=0.0, odl=0.05, material=steel) for _ in range(6)]"},
            {"id": "T1_S3", "title": "Ajouter un disque",
             "theory": "Les disques sont modélisés comme des corps rigides.",
             "objective": "Ajouter un disque au nœud central",
             "code": "disk = rs.DiskElement.from_geometry(n=2, material=steel, width=0.07, i_d=0.05, o_d=0.25)"},
        ]
    },
    "T2_1": {
        "title": "Part 2.1 — Analyses Statiques & Modales",
        "level": "🔵 Intermédiaire",
        "duration": "~20 min",
        "api": ["run_static()", "run_modal()", "run_campbell()"],
        "steps": [
            {"id": "T21_S1", "title": "Analyse statique",
             "theory": "Calcule la déflexion de l'arbre sous son propre poids.",
             "objective": "Calculer la déflexion statique",
             "code": "static = rotor.run_static()\nstatic.plot_deflected_shape()"},
        ]
    }
}

GLOBAL_CSS = """
<style>
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.card { background:#F0F4FF; border-left:5px solid #1F5C8B; border-radius:8px; padding:16px 20px; margin:8px 0; }
.badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:700; margin:2px; }
.badge-blue { background:#1F5C8B; color:#fff; }
.mod-badge { display:inline-block; padding:3px 10px; border-radius:12px; font-size:11px; background:#EBF4FB; color:#1F5C8B; }
</style>
"""

# =============================================================================
# INITIALISATION DE LA SESSION
# =============================================================================

def init_session_state():
    """Initialise toutes les variables de session"""
    defaults = {
        "user_name": "Utilisateur",
        "badges": {},
        "tut_done": set(),
        "current_page": "Tableau de Bord",  # Page par défaut
        "sim_module": "M1",
        "tut_active": "T1",
        "df_shaft": pd.DataFrame([{"L (m)": 0.2, "od (m)": 0.05} for _ in range(5)]),
        "df_disk": pd.DataFrame([{"nœud": 2, "Masse (kg)": 15.12, "Id": 0.025, "Ip": 0.047}]),
        "df_bear": pd.DataFrame([{"nœud": 0, "kxx": 1e6, "kyy": 1e6, "cxx": 0, "cyy": 0}]),
        "rotor": None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

init_session_state()
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; margin-bottom:20px;'>
        <div style='font-size:2.5em;'>⚙️</div>
        <div style='font-size:1.2em; font-weight:bold; color:#1F5C8B;'>RotorLab Suite 1.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.session_state["user_name"] = st.text_input(
        "👤 Votre nom",
        st.session_state.get("user_name", "Utilisateur")
    )
    
    st.markdown("---")
    st.markdown("### 🗺️ Navigation")
    
    # Navigation UNIQUE
    nav_items = [
        ("🏠 Tableau de Bord", "dashboard"),
        ("🎓 Mode Pédagogique", "tutorial"),
        ("🔬 Mode Simulation", "simulation"),
        ("📚 Bibliothèque", "library"),
        ("✨ SmartRotor Copilot", "copilot"),
        ("ℹ️ À propos", "about")
    ]
    
    for label, key in nav_items:
        is_active = st.session_state.get("current_page") == label
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            st.session_state["current_page"] = label
            st.rerun()
    
    st.markdown("---")
    
    # Statut ROSS
    if ROSS_AVAILABLE:
        st.success(f"✅ ROSS {ROSS_VERSION}")
    else:
        st.error("❌ ROSS non installé")
    
    # Rotor actif
    if st.session_state.get("rotor"):
        rotor = st.session_state["rotor"]
        st.markdown("---")
        st.markdown("### 🔧 Rotor actif")
        st.metric("Nœuds", len(rotor.nodes))
        st.metric("Masse", f"{rotor.m:.1f} kg")
    
    st.markdown("---")
    st.caption("RotorLab Suite 1.0 • Propulsé par ROSS")

# =============================================================================
# CONTENU PRINCIPAL
# =============================================================================

current_page = st.session_state.get("current_page", "Tableau de Bord")

# -----------------------------------------------------------------------------
# PAGE : TABLEAU DE BORD
# -----------------------------------------------------------------------------
if current_page == "🏠 Tableau de Bord":
    user_name = st.session_state.get("user_name", "Utilisateur")
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
    
    # Modules
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
            
            if st.button(f"⚙️ Lancer {m_id}", key=f"btn_dash_{m_id}", use_container_width=True):
                st.session_state["current_page"] = "🔬 Mode Simulation"
                st.session_state["sim_module"] = m_id
                st.rerun()
    
    st.markdown("---")
    
    # Tutoriels
    st.markdown("### 🎓 Tutoriels Rapides")
    tut_done = st.session_state.get("tut_done", set())
    tcols = st.columns(4)
    
    for i, (tid, tdata) in enumerate(TUTORIALS.items()):
        done = tid in tut_done
        with tcols[i]:
            st.markdown(f"""
            <div style='background:{"#F0FFF4" if done else "#FFFFFF"}; 
                        border:1px solid #E8E8E8; border-radius:12px; padding:12px;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:8px;'>
                    <span style='background:#1F5C8B; color:white; padding:2px 8px; 
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
        with st.spinner("Chargement..."):
            try:
                comp = rs.compressor_example()
                st.session_state["rotor"] = comp
                st.success("✅ Compresseur chargé avec succès !")
                st.balloons()
            except Exception as e:
                st.error(f"Erreur : {e}")

# -----------------------------------------------------------------------------
# PAGE : MODE PÉDAGOGIQUE
# -----------------------------------------------------------------------------
elif current_page == "🎓 Mode Pédagogique":
    st.title("🎓 Mode Pédagogique — Tutoriels ROSS Officiels")
    
    tut_id = st.session_state.get("tut_active", "T1")
    if tut_id not in TUTORIALS:
        tut_id = "T1"
    
    tut = TUTORIALS[tut_id]
    
    # Sélecteur
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
        <p><b>API ROSS :</b> {api_badges}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation des étapes
    steps = tut["steps"]
    step_key = f"tut_step_{tut_id}"
    current_step = st.session_state.get(step_key, 0)
    
    st.progress((current_step + 1) / len(steps))
    
    step_idx = st.radio(
        "Étapes :",
        range(len(steps)),
        index=min(current_step, len(steps) - 1),
        format_func=lambda i: f"{'✅' if i < current_step else '▶️' if i == current_step else '⬜'} Étape {i+1}: {steps[i]['title']}",
        horizontal=True
    )
    
    step = steps[step_idx]
    st.markdown(f"## Étape {step_idx+1} — {step['title']}")
    
    tab_th, tab_code = st.tabs(["📖 Théorie", "💻 Code"])
    
    with tab_th:
        st.info(step["theory"])
        st.markdown(f"**🎯 Objectif :** {step['objective']}")
    
    with tab_code:
        st.code(step["code"], language="python")
    
    # Navigation
    col_prev, col_next = st.columns(2)
    with col_prev:
        if step_idx > 0 and st.button("⬅️ Précédent", use_container_width=True):
            st.session_state[step_key] = step_idx - 1
            st.rerun()
    with col_next:
        if step_idx < len(steps) - 1 and st.button("Suivant ➡️", type="primary", use_container_width=True):
            st.session_state[step_key] = step_idx + 1
            st.rerun()
    
    if step_idx == len(steps) - 1:
        if st.button("🏆 Terminer ce tutoriel", type="primary", use_container_width=True):
            tut_done = st.session_state.get("tut_done", set())
            tut_done.add(tut_id)
            st.session_state["tut_done"] = tut_done
            st.balloons()
            st.success(f"✅ Tutoriel {tut['title'][:30]} complété !")

# -----------------------------------------------------------------------------
# PAGE : MODE SIMULATION
# -----------------------------------------------------------------------------
elif current_page == "🔬 Mode Simulation":
    st.title("🔬 Mode Simulation")
    
    module_options = ["M1 🏗️ Constructeur", "M2 📊 Statique & Modal", "M3 📈 Campbell", "M4 🌀 Balourd", "M5 ⏱️ Temporel", "M6 📄 Rapport"]
    
    sim_module = st.session_state.get("sim_module", "M1")
    default_idx = 0
    for i, opt in enumerate(module_options):
        if sim_module in opt:
            default_idx = i
            break
    
    selected = st.radio("Module :", module_options, index=default_idx, horizontal=True, label_visibility="collapsed")
    st.session_state["sim_module"] = selected[:2]
    st.markdown("---")
    
    # M1 - Constructeur
    if "M1" in selected:
        st.subheader("🏗️ M1 — Constructeur de Rotor")
        
        tab_mat, tab_arbre, tab_disques, tab_paliers = st.tabs(["Matériau", "Arbre", "Disques", "Paliers"])
        
        with tab_mat:
            mat_name = st.selectbox("Matériau :", list(MATERIALS_DB.keys()))
            props = MATERIALS_DB[mat_name]
            col1, col2, col3 = st.columns(3)
            col1.metric("ρ (kg/m³)", f"{props['rho']:.0f}")
            col2.metric("E (GPa)", f"{props['E']/1e9:.1f}")
            col3.metric("G_s (GPa)", f"{props['G_s']/1e9:.1f}")
        
        with tab_arbre:
            st.session_state.df_shaft = st.data_editor(st.session_state.df_shaft, num_rows="dynamic")
        
        with tab_disques:
            st.session_state.df_disk = st.data_editor(st.session_state.df_disk, num_rows="dynamic")
        
        with tab_paliers:
            st.session_state.df_bear = st.data_editor(st.session_state.df_bear, num_rows="dynamic")
        
        if st.button("🚀 Assembler le rotor", type="primary"):
            if ROSS_AVAILABLE:
                try:
                    mat = rs.Material(name=mat_name, rho=props["rho"], E=props["E"], G_s=props["G_s"])
                    shaft = [rs.ShaftElement(L=row["L (m)"], idl=0, odl=row["od (m)"], material=mat) 
                             for _, row in st.session_state.df_shaft.iterrows()]
                    rotor = rs.Rotor(shaft, [], [])
                    st.session_state["rotor"] = rotor
                    st.success(f"✅ Rotor assemblé — {len(rotor.nodes)} nœuds | Masse : {rotor.m:.2f} kg")
                except Exception as e:
                    st.error(f"Erreur : {e}")
            else:
                st.error("ROSS non disponible")
        
        if st.session_state.get("rotor"):
            st.success("✅ Rotor actif dans la mémoire")
    
    else:
        st.info(f"Module {selected} - En développement")

# -----------------------------------------------------------------------------
# PAGE : BIBLIOTHÈQUE
# -----------------------------------------------------------------------------
elif current_page == "📚 Bibliothèque":
    st.title("📚 Bibliothèque")
    
    tab1, tab2 = st.tabs(["Documentation", "Exemples"])
    
    with tab1:
        st.markdown("""
        ### Documentation ROSS
        
        - **Site officiel :** [ross.readthedocs.io](https://ross.readthedocs.io/)
        - **GitHub :** [github.com/ross-rotordynamics/ross](https://github.com/ross-rotordynamics/ross)
        - **Paper :** Timbó et al. (2020) JOSS 5(48):2120
        """)
    
    with tab2:
        if ROSS_AVAILABLE and st.button("Charger compresseur centrifuge"):
            try:
                comp = rs.compressor_example()
                st.session_state["rotor"] = comp
                st.success("Compresseur chargé !")
            except Exception as e:
                st.error(f"Erreur : {e}")

# -----------------------------------------------------------------------------
# PAGE : SMARTROTOR COPILOT
# -----------------------------------------------------------------------------
elif current_page == "✨ SmartRotor Copilot":
    st.title("✨ SmartRotor Copilot")
    st.info("Assistant IA spécialisé en dynamique des rotors.")
    st.markdown("""
    ### Questions possibles :
    - Comment créer un rotor avec ROSS ?
    - Explique-moi le diagramme de Campbell
    - Comment calculer les vitesses critiques ?
    """)

# -----------------------------------------------------------------------------
# PAGE : À PROPOS
# -----------------------------------------------------------------------------
elif current_page == "ℹ️ À propos":
    st.title("ℹ️ À propos")
    st.markdown("""
    **RotorLab Suite 1.0** est une plateforme avancée de modélisation et de simulation 
    dédiée à la dynamique des rotors.
    
    ### Créateur
    **Pr. Najeh Ben Guedria**
    
    ### Technologies
    - **Framework :** Streamlit
    - **Moteur de calcul :** ROSS (Rotordynamic Open-Source Software)
    - **Visualisation :** Plotly
    - **Rapports :** ReportLab
    
    ### Version
    v1.0 - Mars 2026
    """)
