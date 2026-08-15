from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

VARIANTS = [
    {"name": "Seblak", "category": "Makanan", "price": 10000, "is_active": True, "image": "https://images.unsplash.com/photo-1626082929543-52495d03bb69?w=400&h=300&fit=crop", "description": "Seblak pedas khas Bandung", "spice_level": 3, "favorite": True},
    {"name": "Seblak Biasa (10k)", "category": "Varian - Seblak", "price": 10000, "is_active": True, "image": "", "description": "Seblak dengan harga 10k", "spice_level": 0, "favorite": False},
    {"name": "Seblak Spesial (12k)", "category": "Varian - Seblak", "price": 12000, "is_active": True, "image": "", "description": "Seblak dengan harga 12k", "spice_level": 0, "favorite": False},
    {"name": "Seblak Komplit (15k)", "category": "Varian - Seblak", "price": 15000, "is_active": True, "image": "", "description": "Seblak dengan harga 15k", "spice_level": 0, "favorite": False},
]

print("Inserting seblak into DB...")
for item in VARIANTS:
    try:
        existing = supabase.table("menu_items").select("*").eq("name", item["name"]).execute()
        if len(existing.data) == 0:
            supabase.table("menu_items").insert(item).execute()
            print(f"Inserted: {item['name']}")
        else:
            print(f"Skipped existing: {item['name']}")
    except Exception as e:
        print(f"Error on {item['name']}: {e}")

print("Done")
