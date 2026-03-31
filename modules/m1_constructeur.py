# m1_constructeur.py
# Créé automatiquement dans Colab
# modules/m1_constructeur.py
"""M1 - Constructeur de rotor"""

import streamlit as st
import pandas as pd
import json
import numpy as np
import plotly.graph_objects as go

from core.constants import MATERIALS_DB, BEARING_PRESETS
from core.rotor_builder import RotorBuilder
from core.cache_manager import cache
from ui.components import info_card, metric_card

def render():
    st.subheader("🏗️ M1 — Constructeur de Rotor")
    st.caption("Bibliothèque de matériaux · Validation temps réel · Export TOML/Python")
    
    # Initialisation des tableaux si nécessaire
    if "df_shaft" not in st.session_state:
        _init_tables()
    
    # Barre d'outils
    with st.expander("📁 Gestion des fichiers du Rotor", expanded=True):
        col_new, col_load, col_save = st.columns(3)
        
        with col_new:
            if st.button("📄 Initialiser les tableaux", use_container_width=True):
                _init_tables()
                st.rerun()
        
        with col_load:
            uploaded_file = st.file_uploader("Charger", type=["json"], label_visibility="collapsed")
            if uploaded_file:
                try:
                    data = json.load(uploaded_file)
                    st.session_state.df_shaft = pd.DataFrame(data.get("shaft", []))
                    st.session_state.df_disk = pd.DataFrame(data.get("disks", []))
                    st.session_state.df_bear = pd.DataFrame(data.get("bearings", []))
                    st.success("Données chargées !")
                except Exception as e:
                    st.error(f"Erreur de lecture : {e}")
        
        with col_save:
            current_data = {
                "shaft": st.session_state.df_shaft.to_dict(orient="records"),
                "disks": st.session_state.df_disk.to_dict(orient="records"),
                "bearings": st.session_state.df_bear.to_dict(orient="records")
            }
            json_str = json.dumps(current_data, indent=4)
            st.download_button(
                label="💾 Enregistrer",
                data=json_str,
                file_name="rotor_data.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Onglets principaux
    tab_mat, tab_arbre, tab_disques, tab_paliers = st.tabs([
        "🧱 1. Matériau", "📏 2. Arbre", "💿 3. Disques", "⚙️ 4. Paliers"
    ])
    
    # ... (suite du code M1, adapté pour utiliser les nouvelles structures)
    
    # Bouton d'assemblage
    col_btn, col_msg = st.columns([3, 7])
    with col_btn:
        if st.button("🚀 Assembler le rotor", type="primary", use_container_width=True):
            _build_rotor()
    
    # Affichage du rotor assemblé
    rotor = cache.get("rotor", namespace="simulation")
    if rotor:
        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("Masse totale", f"{rotor.m:.2f}", unit="kg")
        with col2:
            metric_card("Nœuds", len(rotor.nodes))
        with col3:
            L_totale = sum(r.get("L (m)", 0) for r in st.session_state.df_shaft.to_dict('records'))
            metric_card("Longueur", f"{L_totale:.3f}", unit="m")
        
        try:
            fig = rotor.plot_rotor()
            st.plotly_chart(fig, use_container_width=True)
            # Sauvegarde pour le rapport
            st.session_state.img_rotor = fig.to_image(format="png", width=700, height=400)
        except Exception as e:
            st.info(f"Visualisation 3D non disponible : {e}")

def _init_tables():
    """Initialise les tableaux par défaut"""
    st.session_state.df_shaft = pd.DataFrame([
        {"L (m)": 0.2, "id_L (m)": 0.0, "od_L (m)": 0.05, "id_R (m)": 0.0, "od_R (m)": 0.05}
        for _ in range(5)
    ])
    st.session_state.df_disk = pd.DataFrame([
        {"nœud": 2, "Masse (kg)": 15.12, "Id (kg.m²)": 0.025, "Ip (kg.m²)": 0.047}
    ])
    st.session_state.df_bear = pd.DataFrame([
        {"nœud": 0, "Type": "Palier", "kxx": 1e6, "kyy": 1e6, "kxy": 0.0,
         "cxx": 0.0, "cyy": 0.0, "m (kg)": 0.0},
        {"nœud": 5, "Type": "Palier", "kxx": 1e6, "kyy": 1e6, "kxy": 0.0,
         "cxx": 0.0, "cyy": 0.0, "m (kg)": 0.0},
    ])

def _build_rotor():
    """Assemble le rotor à partir des données des tableaux"""
    try:
        import ross as rs
        
        # Récupération du matériau
        mat_name = st.session_state.get("m1_mat", "Acier standard (AISI 1045)")
        props = MATERIALS_DB.get(mat_name, MATERIALS_DB["Acier standard (AISI 1045)"])
        material = rs.Material(
            name=mat_name.replace(" ", "_"),
            rho=props["rho"],
            E=props["E"],
            G_s=props["G_s"]
        )
        
        # Construction de l'arbre
        shaft = []
        for r in st.session_state.df_shaft.to_dict('records'):
            L = float(r.get("L (m)", 0.2))
            idl = float(r.get("id_L (m)", r.get("id (m)", 0.0)))
            odl = float(r.get("od_L (m)", r.get("od (m)", 0.05)))
            idr = float(r.get("id_R (m)", idl))
            odr = float(r.get("od_R (m)", odl))
            
            shaft.append(rs.ShaftElement(
                L=L, idl=idl, odl=odl, idr=idr, odr=odr,
                material=material
            ))
        
        # Construction des disques
        disks = []
        for _, row in st.session_state.df_disk.iterrows():
            disks.append(rs.DiskElement(
                n=int(row["nœud"]),
                m=float(row["Masse (kg)"]),
                Id=float(row["Id (kg.m²)"]),
                Ip=float(row["Ip (kg.m²)"])
            ))
        
        # Construction des paliers
        bearings = []
        for r in st.session_state.df_bear.to_dict('records'):
            n = int(r["nœud"])
            e_type = str(r.get("Type", "Palier")).strip()
            
            if e_type == "Masse":
                m_val = float(r.get("m (kg)", 0.0))
                if m_val > 0:
                    disks.append(rs.DiskElement(n=n, m=m_val, Id=0.0, Ip=0.0))
            else:
                kxx = float(r.get("kxx", 0.0))
                kyy = float(r.get("kyy", 0.0))
                kxy = float(r.get("kxy", 0.0))
                cxx = float(r.get("cxx", 0.0))
                cyy = float(r.get("cyy", 0.0))
                
                bearings.append(rs.BearingElement(
                    n=n, kxx=kxx, kyy=kyy, kxy=kxy, kyx=-kxy,
                    cxx=cxx, cyy=cyy
                ))
        
        # Assemblage final
        rotor = rs.Rotor(shaft, disks, bearings)
        
        cache.set("rotor", rotor, namespace="simulation")
        cache.set("rotor_is_compressor", False, namespace="simulation")
        cache.set("material_props", props, namespace="simulation")
        
        st.success(f"✅ Rotor assemblé — {len(rotor.nodes)} nœuds | Masse : {rotor.m:.2f} kg")
        
    except Exception as e:
        st.error(f"❌ Erreur d'assemblage : {e}")
