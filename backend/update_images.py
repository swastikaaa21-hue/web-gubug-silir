import os
import urllib.parse
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("No Supabase URL or Key provided")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

IMAGE_MAPPING = {
    "Es Kelapa Muda": "/asset/Es Kelapa Muda.jpg",
    "Frozen Food": "/asset/Frozen Food.png",
    "Kentang Goreng": "/asset/Kentang Goreng.png",
    "Lontong Sambel Tahu": "/asset/Lontong Tahu Sambel.png",
    "Mie Goreng": "/asset/Mie Goreng.png",
    "Mie Kuah": "/asset/Mie Kuah.png",
    "Nasi Penyet Ayam": "/asset/Nasi Penyet Ayam.png",
    "Nasi Penyet Tahu Tempe": "/asset/Nasi Penyet Tahu Tempe.png",
    "Nasi Penyet 3T (Tahu, Tempe, Telur)": "/asset/Nasi Penyet Telur Tahu Tempe.png",
    "Nasi Penyet Telur": "/asset/Nasi Penyet Telur.png",
    "Pop Mie": "/asset/Pop Mie.png",
}

def run():
    print("Updating images in Supabase...")
    for name, image_path in IMAGE_MAPPING.items():
        try:
            res = supabase.table("menu_items").update({"image": image_path}).eq("name", name).execute()
            if res.data:
                print(f"Updated {name}")
            else:
                print(f"Item not found: {name}")
        except Exception as e:
            print(f"Error updating {name}: {e}")
    print("Done")

if __name__ == "__main__":
    run()
