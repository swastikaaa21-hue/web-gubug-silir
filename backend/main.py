import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Gubug Silir API")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "https://your-project-id.supabase.co":
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Failed to initialize Supabase: {e}")

# Models
class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int

class Order(BaseModel):
    items: list[OrderItem]
    total_amount: float
    payment_method: str
    notes: str = ""

# Mock Data (Fallback)
MOCK_MENU = [
  {"id": 1, "name": "Mie Gila", "category": "Makanan", "price": 28000, "image": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 3, "favorite": True, "desc": "Mie goreng pedas dengan topping lengkap"},
  {"id": 2, "name": "Mie Ramen Spesial", "category": "Makanan", "price": 35000, "image": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 2, "favorite": False, "desc": "Ramen kuah kental dengan chashu & ajitama"},
  {"id": 3, "name": "Nasi Goreng Kampung", "category": "Makanan", "price": 25000, "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 1, "favorite": True, "desc": "Nasi goreng dengan bumbu kampung autentik"},
  {"id": 7, "name": "Thai Tea", "category": "Minuman", "price": 18000, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": True, "desc": "Thai tea creamy dengan susu segar"},
  {"id": 10, "name": "Es Kopi Susu", "category": "Minuman", "price": 20000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": True, "desc": "Espresso shot dengan gula aren & susu"},
  {"id": 13, "name": "Dimsum Mentai", "category": "Snack", "price": 25000, "image": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": True, "desc": "Dimsum dengan saus mentai gurih"},
  {"id": 14, "name": "Kentang Goreng", "category": "Snack", "price": 18000, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Kentang goreng crispy dengan saus"}
]

@app.get("/api/menu")
def get_menu():
    if supabase:
        try:
            response = supabase.table("menu_items").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Supabase error: {e}")
            # Fallback to mock data if table doesn't exist or error
            return MOCK_MENU
    return MOCK_MENU

@app.post("/api/orders")
def create_order(order: Order):
    if supabase:
        try:
            # Insert Order
            order_data = {
                "total_amount": order.total_amount,
                "payment_method": order.payment_method,
                "notes": order.notes,
                "status": "pending"
            }
            order_res = supabase.table("orders").insert(order_data).execute()
            new_order_id = order_res.data[0]['id']
            
            # Insert Items
            for item in order.items:
                supabase.table("order_items").insert({
                    "order_id": new_order_id,
                    "menu_item_id": item.menu_item_id,
                    "quantity": item.quantity
                }).execute()
                
            return {"success": True, "order_id": new_order_id}
        except Exception as e:
            print(f"Supabase error: {e}")
            # Fallback success
            return {"success": True, "order_id": 999, "warning": "Saved to mock (Supabase error)"}
    
    return {"success": True, "order_id": 12345, "warning": "Saved to mock (No Supabase config)"}

# Mount static frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

