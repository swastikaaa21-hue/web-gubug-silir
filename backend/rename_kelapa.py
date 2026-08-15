from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("Updating Kelapa Utuh variants to include 'dengan'...")

supabase.table("menu_items").update({"name": "Kelapa Utuh dengan Gula Pasir"}).eq("name", "Kelapa Utuh Gula Pasir").execute()
supabase.table("menu_items").update({"name": "Kelapa Utuh dengan Gula Merah"}).eq("name", "Kelapa Utuh Gula Merah").execute()
supabase.table("menu_items").update({"name": "Kelapa Utuh dengan Sirup"}).eq("name", "Kelapa Utuh Sirup").execute()

print("Done")
