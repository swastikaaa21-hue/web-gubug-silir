from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("Deleting Vanilla Blue...")
res = supabase.table("menu_items").delete().eq("name", "Vanilla Blue").execute()
print(f"Deleted {len(res.data)} items: {res.data}")
