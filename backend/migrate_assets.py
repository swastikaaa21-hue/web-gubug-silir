import os
import mimetypes
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file(bucket_name, file_path, object_name):
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    
    try:
        supabase.storage.from_(bucket_name).upload(
            path=object_name,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        print(f"Uploaded {file_path} to {bucket_name}/{object_name}")
    except Exception as e:
        print(f"Skipping {file_path} upload (might already exist): {e}")
        
    return supabase.storage.from_(bucket_name).get_public_url(object_name)

def main():
    # 1. Create web-assets bucket
    try:
        supabase.storage.create_bucket("web-assets")
        supabase.storage.update_bucket("web-assets", {"public": True})
        print("Created web-assets bucket and made it public.")
    except Exception as e:
        print("web-assets bucket might already exist.")
        try:
            supabase.storage.update_bucket("web-assets", {"public": True})
        except:
            pass

    # 2. Upload web assets
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    
    bg_hero_url = upload_file("web-assets", os.path.join(frontend_dir, "bg-hero.png"), "bg-hero.png")
    qris_url = upload_file("web-assets", os.path.join(frontend_dir, "qris.jpeg"), "qris.jpeg")
    
    print(f"bg-hero URL: {bg_hero_url}")
    print(f"qris URL: {qris_url}")
    
    # Write URLs to a text file for frontend replacement step
    with open("web_assets_urls.txt", "w") as f:
        f.write(f"BG_HERO_URL={bg_hero_url}\n")
        f.write(f"QRIS_URL={qris_url}\n")

    # 3 & 4. Upload menu assets and update DB
    asset_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "asset")
    
    if os.path.exists(asset_dir):
        files = os.listdir(asset_dir)
        for filename in files:
            file_path = os.path.join(asset_dir, filename)
            if os.path.isfile(file_path):
                # Upload to menu-images
                public_url = upload_file("menu-images", file_path, filename)
                
                # Fetch menu items that use this image
                # Assuming the DB stores them as `/asset/filename` or `/asset/filename` encoded
                local_path_1 = f"/asset/{filename}"
                local_path_2 = f"/asset/{filename.replace(' ', '%20')}"
                
                res1 = supabase.table("menu_items").select("*").eq("image", local_path_1).execute()
                res2 = supabase.table("menu_items").select("*").eq("image", local_path_2).execute()
                
                items_to_update = res1.data + res2.data
                
                # Remove duplicates just in case
                seen_ids = set()
                unique_items = []
                for item in items_to_update:
                    if item['id'] not in seen_ids:
                        unique_items.append(item)
                        seen_ids.add(item['id'])
                
                for item in unique_items:
                    print(f"Updating menu item {item['id']} ({item['name']}) with public URL...")
                    supabase.table("menu_items").update({"image": public_url}).eq("id", item['id']).execute()

if __name__ == "__main__":
    main()
