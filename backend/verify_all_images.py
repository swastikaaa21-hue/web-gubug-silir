import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Semua file yang ada di /asset
available_assets = {
    "cireng.jpg": "/asset/Cireng.jpg",
    "es kelapa muda.jpg": "/asset/Es Kelapa Muda.jpg",
    "frozen food.png": "/asset/Frozen Food.png",
    "kentang goreng.png": "/asset/Kentang Goreng.png",
    "lontong tahu sambel.png": "/asset/Lontong Tahu Sambel.png",
    "mie goreng.png": "/asset/Mie Goreng.png",
    "mie kuah.png": "/asset/Mie Kuah.png",
    "nasi penyet ayam.png": "/asset/Nasi Penyet Ayam.png",
    "nasi penyet tahu tempe.png": "/asset/Nasi Penyet Tahu Tempe.png",
    "nasi penyet telur tahu tempe.png": "/asset/Nasi Penyet Telur Tahu Tempe.png",
    "nasi penyet telur.png": "/asset/Nasi Penyet Telur.png",
    "pop mie.png": "/asset/Pop Mie.png",
    "sempolan.jpg": "/asset/Sempolan.jpg",
    "es buah.png": "/asset/es buah.png",
    "es milo.png": "/asset/es milo.png",
    "es teh.jpg": "/asset/es teh.jpg",
    "extra joss.jpg": "/asset/extra joss.jpg",
    "gelas.png": "/asset/gelas.png",
    "good day.png": "/asset/good day.png",
    "gorengan.png": "/asset/gorengan.png",
    "jahe.png": "/asset/jahe.png",
    "kopi hitam.png": "/asset/kopi hitam.png",
    "kopi susu.png": "/asset/kopi susu.png",
    "lele.png": "/asset/lele.png",
    "nutrisari.jpg": "/asset/nutrisari.jpg",
    "pop ice.png": "/asset/pop ice.png",
    "seblak.jpg": "/asset/seblak.jpg",
    "white coffe.png": "/asset/white coffe.png",
}

# Mapping nama menu -> nama file asset (lowercase)
menu_to_asset = {
    # Menu utama
    "cireng": "cireng.jpg",
    "kelapa muda utuh": "es kelapa muda.jpg",
    "frozen food": "frozen food.png",
    "kentang goreng": "kentang goreng.png",
    "lontong sambel tahu": "lontong tahu sambel.png",
    "mie goreng": "mie goreng.png",
    "mie kuah": "mie kuah.png",
    "nasi penyet ayam": "nasi penyet ayam.png",
    "nasi penyet tahu tempe": "nasi penyet tahu tempe.png",
    "nasi penyet 3t (tahu, tempe, telur)": "nasi penyet telur tahu tempe.png",
    "nasi penyet telur": "nasi penyet telur.png",
    "pop mie": "pop mie.png",
    "sempolan": "sempolan.jpg",
    "es buah": "es buah.png",           # KOREKSI: pakai es buah.png
    "es milo": "es milo.png",
    "es hilo": "es milo.png",
    "es teh jumbo": "es teh.jpg",
    "extra joss": "extra joss.jpg",
    "es kelapa muda": "gelas.png",
    "es good day": "good day.png",
    "gorengan": "gorengan.png",
    "jahe": "jahe.png",
    "kopi hitam": "kopi hitam.png",
    "kopi susu": "kopi susu.png",
    "nasi penyet lele": "lele.png",
    "nutrisari": "nutrisari.jpg",
    "pop ice": "pop ice.png",           # KOREKSI: pakai pop ice.png
    "seblak prasmanan": "seblak.jpg",
    "white coffee": "white coffe.png",

    # Varian Good Day
    "mocacinno": "good day.png",
    "chococinno": "good day.png",
    "vanilla latte": "good day.png",
    "carrebian nut": "good day.png",
    "coolin": "good day.png",

    # Varian Es Kelapa Muda
    "es kelapa ori": "gelas.png",
    "es kelapa dengan gula pasir": "gelas.png",
    "es kelapa dengan gula merah": "gelas.png",
    "es kelapa dengan sirup": "gelas.png",

    # Varian Kelapa Utuh
    "kelapa utuh ori": "es kelapa muda.jpg",
    "kelapa utuh dengan gula pasir": "es kelapa muda.jpg",
    "kelapa utuh dengan gula merah": "es kelapa muda.jpg",
    "kelapa utuh dengan sirup": "es kelapa muda.jpg",

    # Varian Es Teh
    "es teh biasa (18 oz)": "es teh.jpg",
    "es teh leci": "es teh.jpg",
    "es teh lemon": "es teh.jpg",
    "es milk tea": "es teh.jpg",

    # Varian Extra Joss
    "extra joss biasa": "extra joss.jpg",
    "extra joss susu": "extra joss.jpg",

    # Varian Gorengan
    "tahu asin": "gorengan.png",
    "tela goreng": "gorengan.png",
    "piya piya": "gorengan.png",
    "mendoan": "gorengan.png",
    "tahu isi": "gorengan.png",
    "pisang goreng": "gorengan.png",
    "bakwan jagung": "gorengan.png",

    # Varian Nutrisari
    "sweet orange": "nutrisari.jpg",
    "blewah": "nutrisari.jpg",
    "anggur": "nutrisari.jpg",
    "mangga": "nutrisari.jpg",
    "jeruk peras": "nutrisari.jpg",
    "florida orange": "nutrisari.jpg",

    # Varian Pop Ice - KOREKSI: pakai pop ice.png
    "taro": "pop ice.png",
    "permen karet (bubblegum)": "pop ice.png",
    "melon": "pop ice.png",
    "strawberry": "pop ice.png",
    "coklat": "pop ice.png",
}

# Ambil semua menu dari DB
res = supabase.table("menu_items").select("id, name, image").execute()
all_items = res.data

updated = []
already_ok = []
no_match = []

for item in all_items:
    name_lower = item["name"].lower().strip()
    if name_lower in menu_to_asset:
        asset_file = menu_to_asset[name_lower]
        correct_image = available_assets[asset_file]
        
        if item.get("image") == correct_image:
            already_ok.append(f"  [OK] {item['name']}")
        else:
            supabase.table("menu_items").update({"image": correct_image}).eq("id", item["id"]).execute()
            updated.append(f"  [UPDATED] '{item['name']}': '{item.get('image', '')}' -> '{correct_image}'")
    else:
        no_match.append(f"  [NO MATCH] {item['name']} (category: {item['category']}) -- gambar: {item.get('image', '[kosong]')}")

print(f"\n[OK] Sudah benar ({len(already_ok)}):")
for a in already_ok:
    print(a)

print(f"\n[UPDATE] Diperbarui ({len(updated)}):")
for u in updated:
    print(u)

print(f"\n[NO MATCH] Tidak ada mapping ({len(no_match)}):")
for n in no_match:
    print(n)
