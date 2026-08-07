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
    "Es Kelapa Muda": "/asset/Es%20Kelapa%20Muda.jpg",
    "Frozen Food": "/asset/Frozen%20Food.png",
    "Kentang Goreng": "/asset/Kentang%20Goreng.png",
    "Lontong Sambel Tahu": "/asset/Lontong%20Tahu%20Sambel.png",
    "Mie Goreng": "/asset/Mie%20Goreng.png",
    "Mie Kuah": "/asset/Mie%20Kuah.png",
    "Nasi Penyet Ayam": "/asset/Nasi%20Penyet%20Ayam.png",
    "Nasi Penyet Tahu Tempe": "/asset/Nasi%20Penyet%20Tahu%20Tempe.png",
    "Nasi Penyet 3T (Tahu, Tempe, Telur)": "/asset/Nasi%20Penyet%20Telur%20Tahu%20Tempe.png",
    "Nasi Penyet Telur": "/asset/Nasi%20Penyet%20Telur.png",
    "Pop Mie": "/asset/Pop%20Mie.png",
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
