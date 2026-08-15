from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

res = supabase.table("menu_items").select("*").eq("name", "Seblak").execute()
print(res.data)
