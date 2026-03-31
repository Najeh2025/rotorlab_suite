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
