import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("No Supabase URL or Key provided")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    response = supabase.table("menu_items").update({
        "image": "/asset/gorengan.png"
    }).eq("name", "Gorengan").execute()
    print("Update successful:", response)
except Exception as e:
    print("Error updating database:", e)
