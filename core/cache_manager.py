# cache_manager.py
# Créé automatiquement dans Colab
# core/cache_manager.py
"""Gestionnaire de cache centralisé pour l'application"""

import streamlit as st
from typing import Any, Optional

class CacheManager:
    """
    Gestionnaire de cache unifié.
    Remplace le dictionnaire global _CACHE.
    
    Utilisation:
        cache = CacheManager()
        cache.set("rotor", rotor, namespace="simulation")
        rotor = cache.get("rotor", namespace="simulation")
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_cache()
        return cls._instance
    
    def _init_cache(self):
        """Initialise le cache dans session_state"""
        if "_CACHE_MANAGER" not in st.session_state:
            st.session_state["_CACHE_MANAGER"] = {}
        self._data = st.session_state["_CACHE_MANAGER"]
    
    def _make_key(self, key: str, namespace: str = "global") -> str:
        return f"{namespace}:{key}"
    
    def set(self, key: str, value: Any, namespace: str = "global") -> None:
        """Stocke une valeur dans le cache"""
        full_key = self._make_key(key, namespace)
        self._data[full_key] = value
    
    def get(self, key: str, namespace: str = "global", default: Any = None) -> Any:
        """Récupère une valeur du cache"""
        full_key = self._make_key(key, namespace)
        return self._data.get(full_key, default)
    
    def has(self, key: str, namespace: str = "global") -> bool:
        """Vérifie si une clé existe dans le cache"""
        full_key = self._make_key(key, namespace)
        return full_key in self._data
    
    def delete(self, key: str, namespace: str = "global") -> None:
        """Supprime une clé du cache"""
        full_key = self._make_key(key, namespace)
        if full_key in self._data:
            del self._data[full_key]
    
    def clear_namespace(self, namespace: str) -> None:
        """Supprime toutes les clés d'un namespace"""
        keys_to_delete = [k for k in self._data.keys() if k.startswith(f"{namespace}:")]
        for k in keys_to_delete:
            del self._data[k]
    
    def clear_all(self) -> None:
        """Vide complètement le cache"""
        self._data.clear()
    
    def get_all_keys(self, namespace: str = None) -> list:
        """Retourne toutes les clés (optionnellement filtrées par namespace)"""
        if namespace:
            return [k for k in self._data.keys() if k.startswith(f"{namespace}:")]
        return list(self._data.keys())

# Instance singleton pour l'application
cache = CacheManager()
