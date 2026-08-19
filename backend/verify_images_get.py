import os
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('d:/WEBSITE SILIR/backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
res = supabase.table('menu_items').select('id, name, image').execute()
for item in res.data:
    url = item.get('image')
    if url and 'supabase.co' in url:
        try:
            r = requests.get(url)
            if r.status_code >= 400:
                print(f"FAILED {r.status_code}: {item['name']} -> {url}")
            else:
                if 'application/json' in r.headers.get('Content-Type', ''):
                    print(f"FAILED (JSON Error): {item['name']} -> {url} -> {r.text}")
        except Exception as e:
            print(f"ERROR {e}: {item['name']} -> {url}")
    else:
        print(f"NO URL: {item['name']} -> {url}")
