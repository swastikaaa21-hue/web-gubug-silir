import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Fetch all menu items
res = supabase.table("menu_items").select("id, name, image").execute()
all_items = res.data

# Map: menu name (lowercase) -> image path
# Based on files available in /asset
image_map = {
    "cireng": "/asset/Cireng.jpg",
    "es kelapa muda": "/asset/gelas.png",  # already set
    "frozen food": "/asset/Frozen Food.png",
    "kentang goreng": "/asset/Kentang Goreng.png",
    "lontong tahu sambel": "/asset/Lontong Tahu Sambel.png",
    "mie goreng": "/asset/Mie Goreng.png",
    "mie kuah": "/asset/Mie Kuah.png",
    "nasi penyet ayam": "/asset/Nasi Penyet Ayam.png",
    "nasi penyet tahu tempe": "/asset/Nasi Penyet Tahu Tempe.png",
    "nasi penyet telur tahu tempe": "/asset/Nasi Penyet Telur Tahu Tempe.png",
    "nasi penyet telur": "/asset/Nasi Penyet Telur.png",
    "pop mie": "/asset/Pop Mie.png",
    "sempolan": "/asset/Sempolan.jpg",
    "es campur": "/asset/es campur.png",
    "es milo": "/asset/es milo.png",
    "es teh jumbo": "/asset/es teh.jpg",
    "extra joss": "/asset/extra joss.jpg",
    "es good day": "/asset/good day.png",
    "good day": "/asset/good day.png",
    "gorengan": "/asset/gorengan.png",
    "kopi hitam": "/asset/kopi hitam.png",
    "kopi susu": "/asset/kopi susu.png",
    "ikan lele": "/asset/lele.png",
    "lele": "/asset/lele.png",
    "nutrisari": "/asset/nutrisari.jpg",
    "seblak": "/asset/seblak.jpg",
    "susu jahe": "/asset/susu jahe.png",
    "white coffee": "/asset/white coffe.png",
    "white coffe": "/asset/white coffe.png",
}

updated = []
skipped = []

for item in all_items:
    name_lower = item["name"].lower().strip()
    
    # Skip items that already have a proper image
    if item.get("image") and item["image"].startswith("/asset/"):
        skipped.append(f"  [SKIP] {item['name']} (already has image: {item['image']})")
        continue
    
    if name_lower in image_map:
        new_image = image_map[name_lower]
        supabase.table("menu_items").update({"image": new_image}).eq("id", item["id"]).execute()
        updated.append(f"  [OK] '{item['name']}' -> {new_image}")

print(f"\nUpdated {len(updated)} items:")
for u in updated:
    print(u)

print(f"\nSkipped {len(skipped)} items (already have images):")
for s in skipped:
    print(s)
