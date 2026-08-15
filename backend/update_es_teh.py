import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

# Update image for Es Teh Jumbo
res = supabase.table("menu_items").update({"image": "/asset/es teh.jpg"}).eq("name", "Es Teh Jumbo").execute()
print("Updated Es Teh Jumbo:", res.data)
