from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

print("Moving image to Kelapa Muda Utuh...")
# Set Kelapa Muda Utuh image to the old one
supabase.table("menu_items").update({"image": "/asset/Es Kelapa Muda.jpg"}).eq("name", "Kelapa Muda Utuh").execute()

# Clear Es Kelapa Muda Gelas image
supabase.table("menu_items").update({"image": ""}).eq("name", "Es Kelapa Muda Gelas").execute()

print("Done")
