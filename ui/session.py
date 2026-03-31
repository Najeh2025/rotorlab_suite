# session.py
# Créé automatiquement dans Colab
# ui/session.py
"""Initialisation des variables de session"""

import streamlit as st
import pandas as pd
from typing import Any, Dict

def init_session_state() -> None:
    """Initialise toutes les variables de session nécessaires"""
    
    defaults: Dict[str, Any] = {
        "user_name": "Utilisateur",
        "badges": {},
        "tut_done": set(),
        "sim_count": 0,
        "chat_history": [],
        "nav_page": "🏠 Tableau de Bord",
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
        
        # Images pour le rapport
        "img_rotor": None,
        "img_campbell_plot": None,
        
        # Résultats de calculs
        "df_modal": None,
        "df_campbell": None,
        "df_api": None,
        "api_params": None,
    }
    
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def reset_simulation_state() -> None:
    """Réinitialise l'état de simulation (rotor, résultats)"""
    from core.cache_manager import cache
    cache.clear_namespace("simulation")
    
    # Réinitialisation des résultats
    st.session_state.df_modal = None
    st.session_state.df_campbell = None
    st.session_state.df_api = None
    st.session_state.api_params = None
    st.session_state.img_rotor = None
    st.session_state.img_campbell_plot = None
