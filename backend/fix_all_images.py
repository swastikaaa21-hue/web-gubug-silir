import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Items yang masih pakai URL unsplash (harus diganti) dan yang kosong (harus diisi)
# Foto baru yang tersedia di /asset:
# - es campur.png
# - susu jahe.png

# Mapping koreksi & tambahan gambar
# key = nama menu (lowercase), value = path gambar
updates = {
    # Koreksi: ganti URL unsplash ke asset lokal
    "es hilo": "/asset/es milo.png",          # Hilo mirip milo, gunakan es milo
    "jahe": "/asset/susu jahe.png",            # Ada susu jahe di asset
    "es buah": "/asset/es campur.png",         # Es buah pakai foto es campur

    # Varian - gunakan gambar parent mereka
    # Good Day variants -> good day.png
    "chococinno": "/asset/good day.png",
    "vanilla latte": "/asset/good day.png",
    "carrebian nut": "/asset/good day.png",
    "coolin": "/asset/good day.png",
    "mocacinno": "/asset/good day.png",

    # Varian Es Kelapa Muda -> gelas.png
    "es kelapa dengan gula merah": "/asset/gelas.png",
    "es kelapa dengan sirup": "/asset/gelas.png",
    "es kelapa ori": "/asset/gelas.png",
    "es kelapa dengan gula pasir": "/asset/gelas.png",

    # Varian Es Teh Jumbo -> es teh.jpg
    "es teh leci": "/asset/es teh.jpg",
    "es teh lemon": "/asset/es teh.jpg",
    "es milk tea": "/asset/es teh.jpg",
    "es teh biasa (18 oz)": "/asset/es teh.jpg",

    # Varian Extra Joss -> extra joss.jpg
    "extra joss biasa": "/asset/extra joss.jpg",
    "extra joss susu": "/asset/extra joss.jpg",

    # Varian Gorengan -> gorengan.png
    "tahu asin": "/asset/gorengan.png",
    "tela goreng": "/asset/gorengan.png",
    "piya piya": "/asset/gorengan.png",
    "mendoan": "/asset/gorengan.png",
    "tahu isi": "/asset/gorengan.png",
    "pisang goreng": "/asset/gorengan.png",
    "bakwan jagung": "/asset/gorengan.png",

    # Varian Kelapa Utuh -> Es Kelapa Muda.jpg
    "kelapa utuh dengan gula pasir": "/asset/Es Kelapa Muda.jpg",
    "kelapa utuh dengan sirup": "/asset/Es Kelapa Muda.jpg",
    "kelapa utuh dengan gula merah": "/asset/Es Kelapa Muda.jpg",
    "kelapa utuh ori": "/asset/Es Kelapa Muda.jpg",

    # Varian Nutrisari -> nutrisari.jpg
    "sweet orange": "/asset/nutrisari.jpg",
    "blewah": "/asset/nutrisari.jpg",
    "anggur": "/asset/nutrisari.jpg",
    "mangga": "/asset/nutrisari.jpg",
    "jeruk peras": "/asset/nutrisari.jpg",
    "florida orange": "/asset/nutrisari.jpg",

    # Varian Pop Ice -> pakai es campur (colorful)
    "taro": "/asset/es campur.png",
    "permen karet (bubblegum)": "/asset/es campur.png",
    "melon": "/asset/es campur.png",
    "strawberry": "/asset/es campur.png",
    "coklat": "/asset/es campur.png",
}

res = supabase.table("menu_items").select("id, name, image").execute()
all_items = res.data

updated = []
for item in all_items:
    name_lower = item["name"].lower().strip()
    if name_lower in updates:
        new_image = updates[name_lower]
        supabase.table("menu_items").update({"image": new_image}).eq("id", item["id"]).execute()
        updated.append(f"  [OK] '{item['name']}' -> {new_image}")

print(f"\nUpdated {len(updated)} items:")
for u in updated:
    print(u)
