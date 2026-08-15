from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("menu_items").select("*").eq("category", "Varian - Kelapa Muda Utuh").execute()
for item in res.data:
    print(item)
