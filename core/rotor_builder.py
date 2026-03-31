# rotor_builder.py
# Créé automatiquement dans Colab
# core/rotor_builder.py
"""Constructeur de rotor ROSS avec validation complète"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
import ross as rs

from core.constants import DEFAULT_MATERIAL, MATERIALS_DB

class RotorBuilder:
    """M1 — Constructeur de rotor ROSS avec validation complète."""

    def __init__(self):
        self._shaft: List = []
        self._disks: List = []
        self._bears: List = []
        self._errors: List[str] = []
        self._warnings: List[str] = []
        self.material = DEFAULT_MATERIAL

    def set_material(self, name: str) -> "RotorBuilder":
        """Définit le matériau à partir de la base de données"""
        if not self._check_ross():
            return self
        props = MATERIALS_DB.get(name, MATERIALS_DB["Acier standard (AISI 1045)"])
        try:
            self.material = rs.Material(
                name=name.replace(" ", "_"),
                rho=props["rho"],
                E=props["E"],
                G_s=props["G_s"]
            )
        except Exception as e:
            self._errors.append(f"Matériau invalide : {e}")
        return self

    def add_shaft_from_df(self, df: pd.DataFrame) -> "RotorBuilder":
        """Ajoute des éléments d'arbre à partir d'un DataFrame"""
        if not self._check_ross():
            return self
        self._shaft.clear()
        for i, row in df.iterrows():
            try:
                L = float(row.get("L (m)", row.get("L", 0.2)))
                idl = float(row.get("id_L (m)", row.get("id (m)", 0.0)))
                odl = float(row.get("od_L (m)", row.get("od (m)", 0.05)))
                idr = float(row.get("id_R (m)", idl))
                odr = float(row.get("od_R (m)", odl))
                
                if L <= 0:
                    self._errors.append(f"Élément {i+1} : L doit être > 0")
                    continue
                if idl >= odl or idr >= odr:
                    self._errors.append(f"Élément {i+1} : id doit être < od")
                    continue
                    
                self._shaft.append(rs.ShaftElement(
                    L=L, idl=idl, odl=odl, idr=idr, odr=odr,
                    material=self.material
                ))
            except Exception as e:
                self._errors.append(f"Élément d'arbre {i+1} : {e}")
        return self

    def add_disk(self, node: int, od: float, width: float, id_: float = 0.0) -> "RotorBuilder":
        """Ajoute un disque (masse concentrée)"""
        if not self._check_ross():
            return self
        n_nodes = len(self._shaft) + 1
        if node < 0 or node >= n_nodes:
            self._errors.append(f"Nœud disque {node} invalide — arbre a {n_nodes} nœuds")
            return self
        if id_ >= od:
            self._errors.append(f"Disque nœud {node} : diamètre intérieur ≥ extérieur")
            return self
        try:
            self._disks.append(rs.DiskElement.from_geometry(
                n=node, material=self.material,
                width=width, i_d=id_, o_d=od
            ))
        except Exception as e:
            self._errors.append(f"Disque nœud {node} : {e}")
        return self

    def add_bearing(self, node: int, kxx: float, kyy: float,
                    kxy: float = 0.0, cxx: float = 500.0, cyy: float = 500.0) -> "RotorBuilder":
        """Ajoute un palier"""
        if not self._check_ross():
            return self
        n_nodes = len(self._shaft) + 1
        if node < 0 or node >= n_nodes:
            self._errors.append(f"Nœud palier {node} invalide")
            return self
        if kxx <= 0 or kyy <= 0:
            self._warnings.append(f"Palier nœud {node} : raideur très faible")
        try:
            self._bears.append(rs.BearingElement(
                n=node, kxx=kxx, kyy=kyy, kxy=kxy, kyx=-kxy,
                cxx=cxx, cyy=cyy
            ))
        except Exception as e:
            self._errors.append(f"Palier nœud {node} : {e}")
        return self

    def build(self):
        """Assemble le rotor final"""
        if self._errors:
            return None
        if not self._shaft:
            self._errors.append("Aucun élément d'arbre défini")
            return None
        if not self._bears:
            self._errors.append("Aucun palier défini")
            return None
        try:
            return rs.Rotor(self._shaft, self._disks, self._bears)
        except Exception as e:
            self._errors.append(f"Assemblage impossible : {e}")
            return None

    def _check_ross(self) -> bool:
        """Vérifie la disponibilité de ROSS"""
        try:
            import ross as rs
            return True
        except ImportError:
            self._errors.append("ROSS non disponible")
            return False

    @property
    def errors(self) -> List[str]:
        return self._errors

    @property
    def warnings(self) -> List[str]:
        return self._warnings

    @property
    def n_nodes(self) -> int:
        return len(self._shaft) + 1
