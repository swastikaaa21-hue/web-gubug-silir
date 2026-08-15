from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

VARIANTS = [
    # Teh (Varian - Teh)
    {"name": "Es Teh Biasa (18 Oz)", "category": "Varian - Es Teh Jumbo", "price": 3000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Es Teh Leci", "category": "Varian - Es Teh Jumbo", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Es Teh Lemon", "category": "Varian - Es Teh Jumbo", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Es Milk Tea", "category": "Varian - Es Teh Jumbo", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},

    # Pop Ice (Varian - Pop Ice)
    {"name": "Coklat", "category": "Varian - Pop Ice", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Strawberry", "category": "Varian - Pop Ice", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Vanilla Blue", "category": "Varian - Pop Ice", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Melon", "category": "Varian - Pop Ice", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Permen Karet (Bubblegum)", "category": "Varian - Pop Ice", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Taro", "category": "Varian - Pop Ice", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},

    # Extra Joss
    {"name": "Extra Joss Biasa", "category": "Varian - Extra Joss", "price": 3000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Extra Joss Susu", "category": "Varian - Extra Joss", "price": 6000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},

    # Nutrisari
    {"name": "Jeruk Peras", "category": "Varian - Nutrisari", "price": 4000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Sweet Orange", "category": "Varian - Nutrisari", "price": 4000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Florida Orange", "category": "Varian - Nutrisari", "price": 4000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Blewah", "category": "Varian - Nutrisari", "price": 4000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Anggur", "category": "Varian - Nutrisari", "price": 4000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Mangga", "category": "Varian - Nutrisari", "price": 4000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},

    # Kelapa Muda
    {"name": "Es Kelapa Ori", "category": "Varian - Es Kelapa Muda", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Es Kelapa dengan Gula Pasir", "category": "Varian - Es Kelapa Muda", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Es Kelapa dengan Gula Merah", "category": "Varian - Es Kelapa Muda", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Es Kelapa dengan Sirup", "category": "Varian - Es Kelapa Muda", "price": 5000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},

    # Gorengan
    {"name": "Bakwan Jagung", "category": "Varian - Gorengan", "price": 1000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Piya Piya", "category": "Varian - Gorengan", "price": 1000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Mendoan", "category": "Varian - Gorengan", "price": 1000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Tahu Isi", "category": "Varian - Gorengan", "price": 1000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Tahu Asin", "category": "Varian - Gorengan", "price": 1000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Pisang Goreng", "category": "Varian - Gorengan", "price": 1000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
    {"name": "Tela Goreng", "category": "Varian - Gorengan", "price": 1000, "is_active": True, "image": "", "description": "", "spice_level": 0, "favorite": False},
]

print("Inserting variants into DB...")
for item in VARIANTS:
    try:
        # Avoid duplicate inserts if run multiple times
        existing = supabase.table("menu_items").select("*").eq("name", item["name"]).eq("category", item["category"]).execute()
        if len(existing.data) == 0:
            res = supabase.table("menu_items").insert(item).execute()
            print(f"Inserted: {item['name']}")
        else:
            print(f"Skipped existing: {item['name']}")
    except Exception as e:
        print(f"Error on {item['name']}: {e}")

print("Done")
