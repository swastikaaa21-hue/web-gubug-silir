import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('d:/WEBSITE SILIR/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

res = supabase.table('menu_items').select('id, name, image').execute()
for item in res.data:
    if 'supabase.co' not in (item.get('image') or ''):
        print(f"Missing image URL for {item['id']}: {item['name']} -> {item.get('image')}")
