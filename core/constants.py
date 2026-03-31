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
# core/constants.py (suite)

# =============================================================================
# CATALOGUE TUTORIELS
# =============================================================================

TUTORIALS = {
    "T1": {
        "title": "Part 1 — Création du Modèle (Modeling)",
        "level": "🟢 Débutant",
        "duration": "~15 min",
        "api": ["Material", "ShaftElement", "DiskElement", "BearingElement", "Rotor", "plot_rotor()"],
        "steps": [
            {"id": "T1_S1", "title": "Définir un matériau",
             "theory": "Le matériau définit les propriétés physiques de l'arbre : densité ρ (kg/m³), module d'Young E (Pa) et module de cisaillement G_s (Pa). Ces valeurs déterminent la masse et la rigidité du modèle.",
             "objective": "Créer un matériau Acier avec ρ=7810 kg/m³, E=211 GPa, G_s=81.2 GPa",
             "code": "import ross as rs\nsteel = rs.Material(name='Steel', rho=7810, E=211e9, G_s=81.2e9)\nprint(steel)"},
            {"id": "T1_S2", "title": "Créer les éléments d'arbre",
             "theory": "L'arbre est discrétisé en éléments de poutre de Timoshenko. Chaque ShaftElement est défini par sa longueur L (m), son diamètre intérieur idl et extérieur odl. Les nœuds sont numérotés automatiquement de 0 à N.",
             "objective": "Créer 5 éléments d'arbre de L=0.2m, Ø50mm",
             "code": "shaft = [rs.ShaftElement(L=0.25, idl=0.0, odl=0.05, material=steel)\n         for _ in range(6)]"},
            {"id": "T1_S3", "title": "Ajouter un disque",
             "theory": "Les disques sont modélisés comme des corps rigides. from_geometry() calcule automatiquement la masse et les inerties depuis la géométrie (largeur, diamètre intérieur/extérieur).",
             "objective": "Ajouter un disque Ø250mm au nœud central",
             "code": "disk = rs.DiskElement.from_geometry(\n    n=2, material=steel,\n    width=0.07, i_d=0.05, o_d=0.25\n)"},
            {"id": "T1_S4", "title": "Définir les paliers",
             "theory": "Les paliers sont modélisés comme des éléments ressort-amortisseur linéaires. kxx, kyy = raideurs directes (N/m) ; kxy = raideur croisée ; cxx, cyy = amortissements (N·s/m).",
             "objective": "Créer 2 paliers kxx=kyy=1e7 N/m aux extrémités",
             "code": "bear0 = rs.BearingElement(n=0, kxx=1e7, kyy=1e7, cxx=500, cyy=500)\nbear5 = rs.BearingElement(n=5, kxx=1e7, kyy=1e7, cxx=500, cyy=500)"},
            {"id": "T1_S5", "title": "Assembler et visualiser le rotor",
             "theory": "rs.Rotor() assemble les éléments en construisant les matrices globales M, K, C, G par superposition des contributions élémentaires. plot_rotor() affiche la géométrie 3D interactive.",
             "objective": "Assembler rotor et afficher : masse totale + géométrie 3D",
             "code": "rotor = rs.Rotor(shaft, [disk], [bear0, bear5])\nprint(f'Masse : {rotor.m:.2f} kg')\nrotor.plot_rotor()"},
        ]
    },
    "T2_1": {
        "title": "Part 2.1 — Analyses Statiques & Modales",
        "level": "🔵 Intermédiaire",
        "duration": "~20 min",
        "api": ["run_static()", "run_modal()", "run_campbell()", "run_critical_speed()", "plot_mode_3d()"],
        "steps": [
            {"id": "T21_S1", "title": "Analyse statique (gravité)",
             "theory": "run_static() calcule la déflexion de l'arbre sous son propre poids et celui des disques. Les réactions aux paliers, le diagramme de moment fléchissant et de cisaillement sont automatiquement calculés.",
             "objective": "Calculer et afficher la déflexion statique du rotor",
             "code": "static = rotor.run_static()\nstatic.plot_deflected_shape()\n# Attributs : static.shaft_deflection, static.disk_forces"},
            {"id": "T21_S2", "title": "Analyse modale",
             "theory": "run_modal() résout le problème aux valeurs propres : det(K + jωC − ω²M) = 0. Les valeurs propres complexes donnent les fréquences naturelles (wn, wd) et le décrément logarithmique (log_dec). La direction de précession (avant/arrière) est aussi calculée.",
             "objective": "Calculer les 6 premiers modes à vitesse nulle",
             "code": "modal = rotor.run_modal(speed=0)\nprint('fn (Hz):', modal.wn[:6] / (2*np.pi))\nprint('Log Dec:', modal.log_dec[:6])\nmodal.plot_mode_3d(mode=0)"},
            {"id": "T21_S3", "title": "Diagramme de Campbell",
             "theory": "Le diagramme de Campbell trace les fréquences des modes en fonction de la vitesse de rotation. L'effet gyroscopique sépare les modes de précession avant (FW) et arrière (BW). Les intersections avec la droite 1X donnent les vitesses critiques synchrones.",
             "objective": "Tracer le Campbell de 0 à 10 000 RPM",
             "code": "speeds = np.linspace(0, 10000*np.pi/30, 100)\ncamp = rotor.run_campbell(speeds)\ncamp.plot()"},
            {"id": "T21_S4", "title": "Vitesses critiques",
             "theory": "run_critical_speed() calcule les vitesses critiques non amorties (intersections des modes avec la droite 1X). La marge API 684 exige que la plage opérationnelle soit à ±15% de toute vitesse critique.",
             "objective": "Identifier les vitesses critiques et vérifier la marge API 684",
             "code": "# Vitesses critiques depuis analyse modale\nfn = modal.wn / (2*np.pi)  # Hz\nvc_rpm = fn * 60  # RPM\nprint('Vitesses critiques (RPM):', vc_rpm[:4].round(0))"},
        ]
    },
    "T2_2": {
        "title": "Part 2.2 — Analyses Temporelles & Fréquentielles",
        "level": "🔵 Intermédiaire",
        "duration": "~25 min",
        "api": ["run_unbalance_response()", "run_freq_response()", "run_time_response()", "Probe", "plot_orbit()", "plot_dfft()"],
        "steps": [
            {"id": "T22_S1", "title": "Configuration des sondes (Probe)",
             "theory": "Une sonde virtuelle (Probe) est placée sur un nœud à un angle donné. Elle simule un capteur de déplacement (eddy current probe). Les résultats sont exprimés dans le repère de la sonde : composantes directe et en quadrature.",
             "objective": "Définir 2 sondes à 45° sur le nœud 2",
             "code": "from ross import Probe\nprobe1 = Probe(2, 45.0)   # nœud 2, angle 45°\nprobe2 = Probe(2, 135.0)  # nœud 2, angle 135°"},
            {"id": "T22_S2", "title": "Réponse au balourd",
             "theory": "Un balourd (déséquilibre de masse) génère une force tournante F = m·e·ω². run_unbalance_response() calcule la réponse en fréquence. Le DAF (Dynamic Amplification Factor) = Amplitude_max / Amplitude_statique mesure l'amplification à la résonance.",
             "objective": "Analyser la réponse à un balourd de 0.001 kg·m au nœud 2",
             "code": "resp = rotor.run_unbalance_response(\n    node=[2],\n    magnitude=[0.001],  # kg.m\n    phase=[0.0],\n    frequency_range=np.linspace(0, 5000, 500)\n)\nresp.plot_magnitude(probe=[2, 0])\nresp.plot_phase(probe=[2, 0])"},
            {"id": "T22_S3", "title": "Réponse fréquentielle H(jω)",
             "theory": "run_freq_response() calcule la fonction de transfert H(jω) entre un DDL d'excitation et un DDL de réponse. Le diagramme de Bode (magnitude en dB + phase en degrés) identifie les modes et leurs facteurs d'amortissement.",
             "objective": "Calculer H(jω) entre le DDL 0 (excitation nœud 0, direction X) et le DDL 8 (nœud 2, direction X)",
             "code": "freq_resp = rotor.run_freq_response(\n    inp=0, out=8,\n    frequency_range=np.linspace(0, 5000, 500)\n)\nfreq_resp.plot_bode(inp=0, out=8)"},
            {"id": "T22_S4", "title": "Réponse temporelle et orbites",
             "theory": "run_time_response() intègre l'équation du mouvement dans le domaine temporel (méthode de Newmark). Les orbites décrivent la trajectoire du centre de l'arbre dans le plan XY. La DFFT donne le spectre de vibration.",
             "objective": "Simuler le transitoire de démarrage et afficher les orbites au nœud 2",
             "code": "# Force balourd tournante\nt = np.linspace(0, 2, 1000)\nomega = 3000 * np.pi/30\nF = np.zeros((rotor.ndof, len(t)))\n# Appliquer force au nœud 2\ntime_resp = rotor.run_time_response(\n    speed=omega, force=F, time_range=t\n)\ntime_resp.plot_orbit(node=2)\ntime_resp.plot_dfft(probe=[2, 0], rpm=3000)"},
        ]
    },
    "T4": {
        "title": "Part 4 — Système Multi-Rotors (MultiRotor & GearElement)",
        "level": "🔴 Avancé",
        "duration": "~30 min",
        "api": ["GearElement", "MultiRotor", "couplage latéral-torsionnel"],
        "steps": [
            {"id": "T4_S1", "title": "Création des deux rotors",
             "theory": "Un système engrenage connecte deux rotors tournant à des vitesses différentes. Chaque rotor est créé indépendamment. Le rapport de réduction est déterminé par le nombre de dents.",
             "objective": "Créer le rotor moteur (4 éléments) et le rotor récepteur (3 éléments)",
             "code": "# Rotor 1 (moteur)\nshaft1 = [rs.ShaftElement(L=0.25, idl=0, odl=0.05, material=steel)\n          for _ in range(4)]\n# Rotor 2 (récepteur)\nshaft2 = [rs.ShaftElement(L=0.25, idl=0, odl=0.04, material=steel)\n          for _ in range(3)]"},
            {"id": "T4_S2", "title": "Définir l'élément engrenage",
             "theory": "GearElement modélise le couplage latéral-torsionnel via la ligne d'action des dents. Les paramètres clés sont : pitch_diameter (diamètre de tête), pressure_angle (angle de pression typiquement 20° ou 22.5°) et helix_angle (engrenage hélicoïdal).",
             "objective": "Créer un engrenage droit (pression 20°, Ø100mm) au nœud 2 du rotor 1",
             "code": "gear = rs.GearElement(\n    n=2,\n    pitch_diameter=0.1,\n    pressure_angle=np.radians(20),\n    helix_angle=0.0\n)"},
            {"id": "T4_S3", "title": "Assembler le système MultiRotor",
             "theory": "MultiRotor couple les deux rotors via l'engrenage. Les matrices globales incluent le couplage cinématique imposé par la ligne d'action. L'analyse modale révèle les modes couplés latéraux-torsionnels.",
             "objective": "Assembler le MultiRotor et analyser ses modes couplés",
             "code": "# Note: API MultiRotor dépend de la version ROSS\n# Cf. documentation Part 4 du tutoriel officiel\nrotor1 = rs.Rotor(shaft1, disks1, bears1)\nrotor2 = rs.Rotor(shaft2, disks2, bears2)\n# Couplage via GearElement au nœud spécifié"},
            {"id": "T4_S4", "title": "Analyse Campbell du système couplé",
             "theory": "Le diagramme de Campbell d'un système engrenage montre les modes latéraux de chaque rotor, les modes torsionnels et les modes couplés. Les fréquences d'engrènement apparaissent comme des excitations supplémentaires.",
             "objective": "Tracer le Campbell couplé 0–10 000 RPM (référencé sur rotor 1)",
             "code": "# Campbell du système couplé\nspeeds = np.linspace(0, 10000*np.pi/30, 80)\n# Référencer les vitesses sur le rotor primaire\ncampbell_coupled = multi_rotor.run_campbell(speeds)\ncampbell_coupled.plot()"},
        ]
    },
}
