# components.py
# Créé automatiquement dans Colab
# ui/components.py
"""Composants UI réutilisables (cards, badges, progress, etc.)"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any

def badge(badge_type: str, label: str) -> str:
    """Génère un badge HTML"""
    classes = {
        "gold": "badge-gold",
        "silver": "badge-silver",
        "bronze": "badge-bronze",
        "info": "badge-blue",
        "success": "badge-blue",
        "warning": "badge-gold",
        "error": "badge-bronze"
    }
    css_class = classes.get(badge_type, "badge-blue")
    return f"<span class='badge {css_class}'>{label}</span>"

def card(content: str, style: str = "") -> str:
    """Génère une carte stylisée"""
    return f"<div class='card{style}'>{content}</div>"

def info_card(title: str, content: str, type: str = "info") -> None:
    """Affiche une carte d'information"""
    colors = {
        "info": "#1F5C8B",
        "success": "#22863A",
        "warning": "#C55A11",
        "error": "#C00000"
    }
    bg_colors = {
        "info": "#F0F4FF",
        "success": "#F0FFF4",
        "warning": "#FFF8E1",
        "error": "#FFE6E6"
    }
    st.markdown(f"""
    <div style="background:{bg_colors[type]}; border-left:5px solid {colors[type]}; 
                border-radius:8px; padding:16px 20px; margin:8px 0;">
        <b>{title}</b><br>{content}
    </div>
    """, unsafe_allow_html=True)

def progress_indicator(value: int, max_value: int, label: str = "") -> None:
    """Affiche une barre de progression stylisée"""
    percent = value / max_value * 100 if max_value > 0 else 0
    st.markdown(f"""
    <div style="margin: 10px 0;">
        <div style="background:#E0E0E0; border-radius:10px; height:8px;">
            <div style="background:#1F5C8B; width:{percent}%; height:8px; border-radius:10px;"></div>
        </div>
        <div style="font-size:0.8em; margin-top:4px;">{label} {value}/{max_value}</div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(title: str, value: Any, delta: Optional[float] = None, unit: str = "") -> None:
    """Affiche une carte métrique"""
    delta_html = f"<span style='color:{'#22863A' if delta and delta > 0 else '#C00000'}'>{delta:+.1f}{unit}</span>" if delta else ""
    st.markdown(f"""
    <div style="background:#F8F9FA; border-radius:8px; padding:12px; text-align:center;">
        <div style="font-size:0.85em; color:#666;">{title}</div>
        <div style="font-size:1.8em; font-weight:bold; color:#1F5C8B;">{value}</div>
        <div style="font-size:0.8em;">{unit} {delta_html}</div>
    </div>
    """, unsafe_allow_html=True)

def modal_table(modal) -> pd.DataFrame:
    """Génère un DataFrame à partir des résultats modaux"""
    fn = modal.wn / (2 * np.pi)
    ld = getattr(modal, 'log_dec', np.zeros(len(fn)))
    n = min(8, len(fn))
    
    stab = []
    for v in ld[:n]:
        if v > 0.3:
            stab.append("✅ Très stable")
        elif v > 0.1:
            stab.append("🟡 Stable")
        elif v > 0:
            stab.append("⚠️ Peu amorti")
        else:
            stab.append("❌ INSTABLE")
    
    return pd.DataFrame({
        "Mode": range(1, n+1),
        "fn (Hz)": [f"{v:.3f}" for v in fn[:n]],
        "ωn (rad/s)": [f"{v:.2f}" for v in modal.wn[:n]],
        "Log Dec": [f"{v:.4f}" for v in ld[:n]],
        "Stabilité": stab,
    })
