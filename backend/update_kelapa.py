from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("Updating Es Kelapa Muda (Gelas) description...")
supabase.table("menu_items").update({"description": "Disajikan di dalam gelas dengan kesegaran maksimal."}).eq("name", "Es Kelapa Muda").execute()

# I will set the default price for Kelapa Muda Utuh to 10000.
# The user can edit this in the Admin Panel if needed.
print("Inserting Kelapa Muda Utuh base menu...")
base_menu = {"name": "Kelapa Muda Utuh", "category": "Minuman", "price": 10000, "is_active": True, "image": "", "description": "Kelapa muda utuh langsung dari batoknya.", "spice_level": 0, "favorite": False}
try:
    existing_base = supabase.table("menu_items").select("*").eq("name", base_menu["name"]).execute()
    if len(existing_base.data) == 0:
        res_base = supabase.table("menu_items").insert(base_menu).execute()
        print("Inserted base menu: Kelapa Muda Utuh")
except Exception as e:
    print(f"Error base menu: {e}")

VARIANTS = [
    {"name": "Kelapa Utuh Ori", "category": "Varian - Kelapa Muda Utuh", "price": 10000, "is_active": True, "image": "", "description": "Tanpa tambahan pemanis", "spice_level": 0, "favorite": False},
    {"name": "Kelapa Utuh Gula Pasir", "category": "Varian - Kelapa Muda Utuh", "price": 10000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Kelapa Utuh Gula Merah", "category": "Varian - Kelapa Muda Utuh", "price": 10000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Kelapa Utuh Sirup", "category": "Varian - Kelapa Muda Utuh", "price": 10000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
]

print("Inserting Kelapa Utuh variants...")
for item in VARIANTS:
    existing = supabase.table("menu_items").select("*").eq("name", item["name"]).eq("category", item["category"]).execute()
    if len(existing.data) == 0:
        res = supabase.table("menu_items").insert(item).execute()
        print(f"Inserted: {item['name']}")
    else:
        print(f"Skipped existing: {item['name']}")

print("Done")
