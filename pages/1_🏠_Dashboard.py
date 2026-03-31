# pages/1_🏠_Dashboard.py
"""Page d'accueil / Tableau de bord améliorée"""

import streamlit as st
import pandas as pd
import datetime

from core.cache_manager import cache
from core.constants import TUTORIALS
from ui.components import info_card

def render():
    # En-tête avec message personnalisé
    user_name = st.session_state.get("user_name", "Ingénieur")
    hour = datetime.datetime.now().hour
    
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
    
    # =========================================================
    # ACCÈS RAPIDE AUX MODULES (3 colonnes)
    # =========================================================
    st.markdown("### 🚀 Accès Rapide aux Modules")
    
    modules = [
        ("M1", "🏗️ Constructeur", "Géométrie, Matériaux, Paliers", "✅", "#1F5C8B"),
        ("M2", "📊 Statique & Modal", "Déflexion, Fréquences propres", "✅", "#22863A"),
        ("M3", "📈 Campbell", "Stabilité, Vitesses critiques, API", "✅", "#C55A11"),
        ("M4", "🌀 Balourd & H(jω)", "Bode, Nyquist, Norme ISO 1940", "✅", "#7B1FA2"),
        ("M5", "⏱️ Temporel", "Défauts, Cascade 3D", "✅", "#117A8B"),
        ("M6", "📄 Rapport & Export", "PDF, Excel, HTML", "✅", "#C00000"),
    ]
    
    cols = st.columns(3)
    for i, (m_id, title, desc, status, color) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div style='background:#FFFFFF; 
                        border:1px solid #E8E8E8;
                        border-radius:12px; 
                        padding:14px 12px; 
                        margin-bottom:12px;
                        transition: all 0.2s ease;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                    <div>
                        <span style='background:{color}20; color:{color}; 
                                   padding:4px 10px; border-radius:20px; 
                                   font-size:12px; font-weight:bold;'>
                            {m_id}
                        </span>
                    </div>
                    <span style='color:#22863A; font-size:14px;'>{status}</span>
                </div>
                <div style='font-weight:600; font-size:1em; margin:8px 0 4px;'>{title}</div>
                <div style='font-size:0.75em; color:#888; line-height:1.3;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"⚙️ Lancer {m_id}", key=f"btn_dash_{m_id}", 
                         use_container_width=True, type="primary"):
                st.session_state["nav_page"] = "🔬 Mode Simulation"
                st.session_state["sim_module"] = m_id
                st.rerun()
    
    st.markdown("---")
    
    # =========================================================
    # TUTORIELS RAPIDES (4 colonnes améliorées)
    # =========================================================
    st.markdown("### 🎓 Tutoriels Rapides")
    
    tut_done = st.session_state.get("tut_done", set())
    level_config = {
        "🟢 Débutant": {"color": "#22863A", "bg": "#F0FFF4"},
        "🔵 Intermédiaire": {"color": "#1F5C8B", "bg": "#F0F4FF"},
        "🔴 Avancé": {"color": "#C55A11", "bg": "#FFF8E8"}
    }
    
    tcols = st.columns(4)
    for i, (tid, tdata) in enumerate(TUTORIALS.items()):
        done = tid in tut_done
        config = level_config.get(tdata['level'], level_config["🔵 Intermédiaire"])
        
        with tcols[i]:
            st.markdown(f"""
            <div style='background:{config["bg"] if not done else "#F0FFF4"};
                        border-radius:12px;
                        border:1px solid {config["color"]}30;
                        padding:12px;
                        margin-bottom:10px;
                        transition: transform 0.2s;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                    <span style='background:{config["color"]}; color:white; 
                                 padding:2px 10px; border-radius:20px; 
                                 font-size:10px; font-weight:bold;'>
                        {tdata['level']}
                    </span>
                    <span style='font-size:20px;'>{'✅' if done else '📘'}</span>
                </div>
                <div style='font-weight:600; font-size:0.9em; margin-bottom:6px; line-height:1.3;'>
                    {tdata['title'][:40]}{"..." if len(tdata['title']) > 40 else ""}
                </div>
                <div style='font-size:10px; color:#888; margin-bottom:12px;'>
                    ⏱ {tdata['duration']} • {len(tdata['steps'])} étapes
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            btn_text = "📖 Reprendre" if done else "📖 Démarrer"
            if st.button(btn_text, key=f"btn_dash_tut_{tid}", use_container_width=True):
                st.session_state["nav_page"] = "🎓 Mode Pédagogique"
                st.session_state["tut_active"] = tid
                st.rerun()
    
    st.markdown("---")
    
    # =========================================================
    # CAS D'ÉTUDE INDUSTRIEL (amélioré)
    # =========================================================
    st.markdown("### 🏭 Cas d'Étude Industriel")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div style='background:#F8FAFE; border-radius:12px; padding:16px 20px; 
                    border-left:4px solid #1F5C8B;'>
            <div style='font-weight:600; font-size:1.1em; margin-bottom:8px;'>
                🔧 Compresseur Centrifuge
            </div>
            <div style='font-size:0.85em; color:#555; margin-bottom:12px;'>
                <b>Modèle industriel complet</b> avec 56 nœuds, 5 roues (disques), 
                paliers hydrodynamiques. Conforme aux standards API 684.
            </div>
            <ul style='margin:0 0 12px 0; padding-left:20px; font-size:0.8em; color:#666;'>
                <li>56 nœuds • 245 kg</li>
                <li>Analyse Campbell 0-15000 RPM</li>
                <li>Balourd et réponse temporelle</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔌 Charger Compresseur Centrifuge", use_container_width=True, type="primary"):
            _load_compressor_example()
    
    with col_right:
        st.markdown("""
        <div style='background:linear-gradient(135deg, #1F5C8B05, #FFFFFF); 
                    border-radius:12px; padding:16px; text-align:center;
                    border:1px solid #E8E8E8;'>
            <div style='font-size:2.5em;'>🏭</div>
            <div style='font-weight:600; margin:8px 0 4px;'>Compresseur Centrifuge</div>
            <div style='font-size:0.7em; color:#888;'>56 nœuds • 245 kg</div>
            <div style='margin-top:12px;'>
                <span class='badge badge-blue' style='font-size:10px;'>API 684</span>
                <span class='badge badge-blue' style='font-size:10px;'>ISO 1940</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def _load_compressor_example():
    """Charge l'exemple de compresseur"""
    try:
        import ross as rs
        
        with st.spinner("Chargement du modèle industriel..."):
            comp = rs.compressor_example()
            cache.set("rotor", comp, namespace="simulation")
            cache.set("rotor_is_compressor", True, namespace="simulation")
            
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
        st.error(f"Erreur lors du chargement : {e}")

if __name__ == "__main__":
    render()
