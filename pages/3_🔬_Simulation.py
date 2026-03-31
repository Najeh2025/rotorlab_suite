# 3_🔬_Simulation.py
# Créé automatiquement dans Colab
# pages_disabled/3_🔬_Simulation.py
"""Page principale du mode simulation - Orchestre les modules M1 à M6"""

import streamlit as st

from modules import m1_constructeur, m2_statique_modal, m3_campbell
from modules import m4_balourd, m5_temporel_defauts, m6_rapport
from core.cache_manager import cache

def render():
    st.title("🔬 Mode Simulation")
    
    module_options = [
        "M1 🏗️ Constructeur",
        "M2 📊 Statique & Modal",
        "M3 📈 Campbell & Stabilité",
        "M4 🌀 Balourd",
        "M5 ⏱️ Temporel",
        "M6 📄 Rapport PDF"
    ]
    
    # Récupération du module demandé
    default_idx = 0
    sim_module = st.session_state.get("sim_module", "M1")
    for i, opt in enumerate(module_options):
        if sim_module in opt:
            default_idx = i
            break
    
    selected_mod = st.radio(
        "Workflow d'analyse :",
        module_options,
        index=default_idx,
        horizontal=True,
        key="sim_mod_radio",
        label_visibility="collapsed"
    )
    
    st.session_state["sim_module"] = selected_mod[:2]
    st.markdown("---")
    
    # Routage vers le module approprié
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

if __name__ == "__main__":
    render()
