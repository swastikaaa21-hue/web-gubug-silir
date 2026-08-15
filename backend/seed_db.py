import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import asyncio

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("No Supabase URL or Key provided")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Mock Menu from main.py
MOCK_MENU = [
    {"name": "Seblak Prasmanan", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1596649283733-1256956795f7?w=400&h=300&fit=crop", "badge": "spicy", "spice_level": 2, "favorite": True, "description": "Seblak dengan topping prasmanan pilihan (mulai 1K)"},
    {"name": "Nasi Penyet Tahu Tempe", "category": "Makanan", "price": 7000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spice_level": 1, "favorite": False, "description": "Nasi penyet dengan tahu dan tempe goreng"},
    {"name": "Nasi Penyet Telur", "category": "Makanan", "price": 9000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spice_level": 1, "favorite": False, "description": "Nasi penyet dengan telur dadar/ceplok"},
    {"name": "Nasi Penyet 3T (Tahu, Tempe, Telur)", "category": "Makanan", "price": 12000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spice_level": 2, "favorite": True, "description": "Nasi penyet komplit tahu, tempe, dan telur"},
    {"name": "Nasi Penyet Ayam", "category": "Makanan", "price": 12000, "image": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&h=300&fit=crop", "badge": "spicy", "spice_level": 2, "favorite": True, "description": "Nasi penyet dengan ayam goreng gurih"},
    {"name": "Nasi Penyet Lele", "category": "Makanan", "price": 12000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spice_level": 2, "favorite": False, "description": "Nasi penyet dengan lele goreng garing"},
    {"name": "Mie Goreng", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Indomie goreng nikmat"},
    {"name": "Mie Kuah", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Indomie kuah hangat"},
    {"name": "Pop Mie", "category": "Makanan", "price": 8000, "image": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Mie cup praktis"},
    {"name": "Lontong Sambel Tahu", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spice_level": 2, "favorite": False, "description": "Lontong dengan tahu dan sambal pedas"},
    {"name": "Frozen Food", "category": "Snack", "price": 10000, "image": "https://images.unsplash.com/photo-1528736235302-52922df5c122?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Aneka sosis, nugget goreng"},
    {"name": "Gorengan", "category": "Snack", "price": 1000, "image": "/asset/gorengan.png", "badge": None, "spice_level": 0, "favorite": False, "description": "Aneka gorengan hangat"},
    {"name": "Kentang Goreng", "category": "Snack", "price": 8000, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": True, "description": "Kentang goreng renyah"},
    {"name": "Cireng", "category": "Snack", "price": 2000, "image": "/asset/Cireng.jpg", "badge": None, "spice_level": 0, "favorite": False, "description": "Camilan cireng isi renyah"},
    {"name": "Sempolan", "category": "Snack", "price": 2000, "image": "/asset/Sempolan.jpg", "badge": None, "spice_level": 0, "favorite": False, "description": "Camilan sempolan gurih"},
    {"name": "Es Kelapa Muda", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": True, "description": "Es kelapa muda segar"},
    {"name": "Es Teh Jumbo", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": True, "description": "Es teh manis porsi jumbo"},
    {"name": "Kelapa Muda Utuh + Gula", "category": "Minuman", "price": 10000, "image": "https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Kelapa muda segar disajikan utuh dengan gula"},
    {"name": "Kelapa Muda Utuh + Sirup", "category": "Minuman", "price": 12000, "image": "https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Kelapa muda segar disajikan utuh dengan sirup"},
    {"name": "Es Buah", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1519996521430-02b798c1d881?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": True, "description": "Es buah segar pelepas dahaga"},
    {"name": "Es Good Day", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Kopi Good Day dingin"},
    {"name": "Es Cappucino", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Cappucino dingin"},
    {"name": "Es Milo", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1542990253-0d0f5be5f0ed?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": True, "description": "Susu coklat Milo dingin"},
    {"name": "Pop Ice", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1572490122747-3968b75bf699?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Minuman blender rasa buah/susu"},
    {"name": "Es Hilo", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1542990253-0d0f5be5f0ed?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Susu Hilo dingin"},
    {"name": "Kopi Susu", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Kopi dicampur susu"},
    {"name": "White Coffee", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Kopi instan Luwak White Koffie"},
    {"name": "Extra Joss", "category": "Minuman", "price": 3000, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Minuman berenergi"},
    {"name": "Kopi Hitam", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1550186981-d102bc0f7190?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Kopi hitam panas/dingin"},
    {"name": "Jahe", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=400&h=300&fit=crop", "badge": None, "spice_level": 0, "favorite": False, "description": "Minuman jahe hangat"},
    {"name": "Nutrisari", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&h=300&fit=crop", "badge": "ice", "spice_level": 0, "favorite": False, "description": "Minuman segar rasa jeruk/buah lainnya"}
]

def run():
    print("Seeding to Supabase...")
    for item in MOCK_MENU:
        try:
            res = supabase.table("menu_items").insert(item).execute()
            print(f"Added {item['name']}")
        except Exception as e:
            print(f"Error adding {item['name']}: {e}")
    print("Done")

if __name__ == "__main__":
    run()
