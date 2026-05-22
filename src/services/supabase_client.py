# src/services/supabase_client.py
import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = "https://vpdbqgrjzhwrqmvmjrlh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZGJxZ3Jqemh3cnFtdm1qcmxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMDA4MDIsImV4cCI6MjA5NDg3NjgwMn0.YXh9z_RDR0JKu0KCVKiv56tR2PFfFv6SjN9dbVya3xw"

@st.cache_resource
def init_supabase() -> Client:
    """Inicializa y cachea la instancia del cliente para todo el ciclo de la app"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Instancia global lista para ser importada por tus otros servicios
supabase = init_supabase()