import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    print("Creating bucket 'menu-images'...")
    res = supabase.storage.create_bucket("menu-images")
    print("Create response:", res)
except Exception as e:
    print("Error:", e)
