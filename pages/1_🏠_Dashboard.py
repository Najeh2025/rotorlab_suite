# 1_🏠_Dashboard.py
# Créé automatiquement dans Colab
# pages/1_🏠_Dashboard.py
"""Page d'accueil / Tableau de bord"""

import streamlit as st
import pandas as pd

from core.cache_manager import cache
from core.constants import TUTORIALS  # À déplacer depuis l'original
from ui.components import badge, info_card

def render():
    st.markdown("""
    <div style='text-align:center; padding:5px 0 20px'>
      <h1 style='color:#1F5C8B; font-size:3em; margin:0; font-weight:800;'>
        RotorLab Suite 1.0
      </h1>
      <p style='color:#666; font-size:1.2em; font-weight:500; margin:0'>
        Plateforme d'Ingénierie Avancée pour la Dynamique des Rotors
      </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Accès rapide aux modules
    st.markdown("### 🚀 Accès Rapide aux Modules")
    modules = [
        ("M1", "🏗️ Constructeur", "Géométrie, Matériaux, Paliers"),
        ("M2", "📊 Statique & Modal", "Déflexion, Fréquences propres"),
        ("M3", "📈 Campbell", "Stabilité, Vitesses critiques, API"),
        ("M4", "🌀 Balourd & H(jω)", "Bode, Nyquist, Norme ISO 1940"),
        ("M5", "⏱️ Temporel", "Défauts, Cascade 3D (Waterfall)"),
        ("M6", "📄 Rapport & Export", "Génération du document PDF final"),
    ]
    
    cols = st.columns(3)
    for i, (m_id, title, desc) in enumerate(modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div style='background:#f8f9fa; padding:10px 15px; border-radius:6px; 
                        border-left:4px solid #1F5C8B; margin-bottom:5px;'>
                <b style='font-size:1.1em;'>{m_id} {title}</b><br>
                <span style='font-size:0.85em; color:#666;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"⚙️ Lancer {m_id}", key=f"btn_dash_{m_id}", 
                         use_container_width=True, type="primary"):
                st.session_state["nav_page"] = "🔬 Mode Simulation"
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
            status = "✅" if done else "▶️"
            card_color = "#22863A" if done else "#1F5C8B"
            
            st.markdown(f"""
            <div class='card' style='padding:10px; border-left-color:{card_color}; margin-bottom:5px;'>
                <small>{status} <b>{tdata['level']}</b></small><br>
                <span style='font-size:0.8em;'>{tdata['title'][:35]}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📖 Démarrer", key=f"btn_dash_tut_{tid}", 
                         use_container_width=True):
                st.session_state["nav_page"] = "🎓 Mode Pédagogique"
                st.session_state["tut_active"] = tid
                st.rerun()
    
    st.markdown("---")
    
    # Cas d'étude
    st.markdown("### 🏭 Cas d'Étude Industriel")
    info_card(
        "Compresseur centrifuge",
        "Validation sur un système réel : chargez le modèle complet d'un compresseur centrifuge à 56 nœuds."
    )
    
    try:
        import ross as rs
        if st.button("🔌 Charger Compresseur Centrifuge", use_container_width=True, type="primary"):
            with st.spinner("Chargement..."):
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
                
                st.success("✅ Compresseur chargé ! Allez dans Mode Simulation pour l'analyser.")
                st.rerun()
    except Exception as e:
        st.error(f"Impossible de charger l'exemple : {e}")

if __name__ == "__main__":
    render()
