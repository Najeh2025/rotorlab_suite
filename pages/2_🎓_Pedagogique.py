# 2_🎓_Pedagogique.py
# Créé automatiquement dans Colab
# pages_disabled/2_🎓_Pedagogique.py
"""Mode Pédagogique - Tutoriels interactifs"""

import streamlit as st

from core.constants import TUTORIALS
from core.cache_manager import cache
from ui.components import progress_indicator, info_card

def render():
    st.title("🎓 Mode Pédagogique — Tutoriels ROSS Officiels")
    
    # Sélection du tutoriel
    tut_keys = list(TUTORIALS.keys())
    default_idx = 0
    
    if "tut_active" in st.session_state and st.session_state["tut_active"] in tut_keys:
        default_idx = tut_keys.index(st.session_state["tut_active"])
    
    tut_id = st.selectbox(
        "Sélectionnez un tutoriel :",
        tut_keys,
        index=default_idx,
        format_func=lambda x: f"{TUTORIALS[x]['level']} — {TUTORIALS[x]['title'][:50]}..."
    )
    
    st.session_state["tut_active"] = tut_id
    tut = TUTORIALS[tut_id]
    
    # En-tête
    api_badges = "".join(f"<span class='mod-badge'>{a}</span>" for a in tut["api"])
    st.markdown(f"""
    <div class='card'>
      <h2 style='color:#1F5C8B; margin:0'>{tut['title']}</h2>
      <p>{tut['level']} &nbsp;|&nbsp; ⏱ {tut['duration']}</p>
      <p><b>API ROSS utilisée :</b> {api_badges}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation par étapes
    steps = tut["steps"]
    n_steps = len(steps)
    done_key = f"tut_step_{tut_id}"
    current = st.session_state.get(done_key, 0)
    
    progress_indicator(current, n_steps, f"Progression")
    
    # ... (reste du code inchangé)

if __name__ == "__main__":
    render()
