import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('d:/WEBSITE SILIR/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
res = supabase.table('menu_items').select('id, name, image').execute()
for item in res.data:
    print(f"{item['id']}: {item['name']} -> {item.get('image')}")
