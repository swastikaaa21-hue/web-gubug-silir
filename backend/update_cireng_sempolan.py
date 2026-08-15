import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Delete existing Cireng / Sempolan
supabase.table("menu_items").delete().eq("name", "Cireng / Sempolan").execute()

# 2. Insert Cireng
cireng = {
    "name": "Cireng",
    "category": "Snack",
    "price": 2000,
    "image": "/asset/Cireng.jpg",
    "badge": None,
    "spice_level": 0,
    "favorite": False,
    "description": "Camilan cireng renyah"
}

# 3. Insert Sempolan
sempolan = {
    "name": "Sempolan",
    "category": "Snack",
    "price": 2000,
    "image": "/asset/Sempolan.jpg",
    "badge": None,
    "spice_level": 0,
    "favorite": False,
    "description": "Camilan sempolan gurih"
}

supabase.table("menu_items").insert([cireng, sempolan]).execute()
print("Successfully split Cireng / Sempolan into two items and updated images.")
