# core/constants.py
"""Constantes globales de l'application (matériaux, paliers, etc.)"""

MATERIALS_DB = {
    "Acier standard (AISI 1045)": {"rho": 7810.0, "E": 211e9, "G_s": 81.2e9},
    "Acier inoxydable (316L)":     {"rho": 7990.0, "E": 193e9, "G_s": 74.0e9},
    "Aluminium (7075-T6)":         {"rho": 2810.0, "E":  72e9, "G_s": 27.0e9},
    "Titane (Ti-6Al-4V)":          {"rho": 4430.0, "E": 114e9, "G_s": 44.0e9},
    "Inconel 718":                 {"rho": 8220.0, "E": 200e9, "G_s": 77.0e9},
    "Personnalisé":                {"rho": 7810.0, "E": 211e9, "G_s": 81.2e9},
}

BEARING_PRESETS = {
    "Roulement à billes":         {"kxx":1e7,"kyy":1e7,"kxy":0.0,"cxx":500.0,"cyy":500.0},
    "Palier lisse hydrodynamique":{"kxx":1e7,"kyy":5e6,"kxy":2e6,"cxx":2000.0,"cyy":2000.0},
    "Support souple (amortisseur)":{"kxx":1e6,"kyy":1e6,"kxy":0.0,"cxx":5000.0,"cyy":5000.0},
    "Palier rigide (encastrement)":{"kxx":1e9,"kyy":1e9,"kxy":0.0,"cxx":100.0,"cyy":100.0},
    "Personnalisé":               {"kxx":1e7,"kyy":1e7,"kxy":0.0,"cxx":500.0,"cyy":500.0},
}

# Matériau par défaut (créé dynamiquement)
DEFAULT_MATERIAL = None  # Sera initialisé à l'import si ROSS dispo

# CSS global
GLOBAL_CSS = """
<style>
.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { height: 44px; font-weight: 600; border-radius: 8px 8px 0 0; }
.card { background:#F0F4FF; border-left:5px solid #1F5C8B; border-radius:8px; padding:16px 20px; margin:8px 0; }
.card-green  { background:#F0FFF4; border-left:5px solid #22863A; }
.card-orange { background:#FFF8E1; border-left:5px solid #C55A11; }
.card-red    { background:#FFE6E6; border-left:5px solid #C00000; }
.badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:700; margin:2px; }
.badge-gold   { background:#FFD700; color:#7A5700; }
.badge-silver { background:#C0C0C0; color:#3A3A3A; }
.badge-bronze { background:#CD7F32; color:#fff; }
.badge-blue   { background:#1F5C8B; color:#fff; }
.mod-badge { display:inline-block; padding:3px 10px; border-radius:12px; font-size:11px;
             font-weight:600; margin:2px; background:#EBF4FB; color:#1F5C8B; border:1px solid #AED6F1; }
.code-box { background:#1E1E1E; color:#D4D4D4; padding:12px 16px; border-radius:6px;
            font-family:monospace; font-size:12px; margin:8px 0; overflow-x:auto; }
.status-ok   { background:#E6FFE6; border:1px solid #22863A; border-radius:6px; padding:8px 14px; }
.status-warn { background:#FFF8E1; border:1px solid #F9A825; border-radius:6px; padding:8px 14px; }
.status-err  { background:#FFE6E6; border:1px solid #C00000; border-radius:6px; padding:8px 14px; }
</style>
"""

# Initialisation du matériau par défaut
def init_default_material():
    global DEFAULT_MATERIAL
    try:
        import ross as rs
        DEFAULT_MATERIAL = rs.Material(name="Steel", rho=7810, E=211e9, G_s=81.2e9)
    except Exception:
        DEFAULT_MATERIAL = None
    return DEFAULT_MATERIAL
