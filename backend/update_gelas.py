import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table("menu_items").select("id, name, image").like("name", "%Gelas%").execute()
for item in res.data:
    old_name = item["name"]
    new_name = old_name.replace(" Gelas", "").replace("Gelas", "").strip()
    
    update_data = {"name": new_name}
    if "Es Kelapa Muda" in old_name:
        update_data["image"] = "/asset/gelas.png"
        
    print(f"Updating '{old_name}' -> '{new_name}' with image {update_data.get('image', 'unchanged')}")
    supabase.table("menu_items").update(update_data).eq("id", item["id"]).execute()
