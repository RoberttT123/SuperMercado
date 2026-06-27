from supabase import create_client

SUPABASE_URL = "https://vpdbqgrjzhwrqmvmjrlh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwZGJxZ3Jqemh3cnFtdm1qcmxoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkzMDA4MDIsImV4cCI6MjA5NDg3NjgwMn0.YXh9z_RDR0JKu0KCVKiv56tR2PFfFv6SjN9dbVya3xw"  # Settings → API → anon public

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)