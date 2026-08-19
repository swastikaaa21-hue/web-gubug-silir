import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    print("Updating bucket 'menu-images' to public...")
    res = supabase.storage.update_bucket("menu-images", {"public": True})
    print("Update response:", res)
except Exception as e:
    print("Error:", e)
