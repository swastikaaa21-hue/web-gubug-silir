from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("Updating Es Kelapa Muda base menu...")
supabase.table("menu_items").update({"name": "Es Kelapa Muda Gelas"}).eq("name", "Es Kelapa Muda").execute()

print("Updating Es Kelapa Muda variants...")
supabase.table("menu_items").update({"name": "Es Kelapa Ori Gelas"}).eq("name", "Es Kelapa Ori").execute()
supabase.table("menu_items").update({"name": "Es Kelapa dengan Gula Pasir Gelas"}).eq("name", "Es Kelapa dengan Gula Pasir").execute()
supabase.table("menu_items").update({"name": "Es Kelapa dengan Gula Merah Gelas"}).eq("name", "Es Kelapa dengan Gula Merah").execute()
supabase.table("menu_items").update({"name": "Es Kelapa dengan Sirup Gelas"}).eq("name", "Es Kelapa dengan Sirup").execute()

print("Done")
