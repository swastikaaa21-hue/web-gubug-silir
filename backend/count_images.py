import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('d:/WEBSITE SILIR/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
res = supabase.table('menu_items').select('id, name, image').execute()
supabase_count = sum(1 for item in res.data if 'supabase.co' in (item.get('image') or ''))
total_count = len(res.data)
empty_count = sum(1 for item in res.data if not item.get('image'))
asset_count = sum(1 for item in res.data if '/asset/' in (item.get('image') or ''))

print(f"Total: {total_count}")
print(f"Supabase URLs: {supabase_count}")
print(f"Empty/Null: {empty_count}")
print(f"/asset/ URLs: {asset_count}")

# Print items that don't have supabase.co
for item in res.data:
    if 'supabase.co' not in (item.get('image') or ''):
        print(f"NOT SUPABASE: {item['id']}: {item['name']} -> {item.get('image')}")
