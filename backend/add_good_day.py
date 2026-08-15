import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

variants = [
    "Mocacinno",
    "Chococinno",
    "Vanilla Latte",
    "Carrebian Nut",
    "Coolin"
]

parent_price = 5000
category = "Varian - Es Good Day"

for variant in variants:
    # Check if exists
    existing = supabase.table("menu_items").select("*").eq("name", variant).eq("category", category).execute()
    if not existing.data:
        data = {
            "name": variant,
            "category": category,
            "price": parent_price,
            "is_active": True,
            "description": f"Varian {variant}"
        }
        supabase.table("menu_items").insert(data).execute()
        print(f"Added {variant}")
    else:
        print(f"{variant} already exists")
