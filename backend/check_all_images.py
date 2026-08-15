import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("menu_items").select("id, name, category, image").order("category").execute()
for item in res.data:
    img = item["image"] if item["image"] else "[KOSONG]"
    print(f"  [{item['category']}] {item['name']} --> {img}")
