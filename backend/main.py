import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import midtransclient
from fastapi import Request

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

# Konfigurasi Midtrans
MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY", "SB-Mid-server-XXXXXXXX")
snap = midtransclient.Snap(
    is_production=False,
    server_key=MIDTRANS_SERVER_KEY
)

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
    {"id": 1, "name": "Seblak Prasmanan", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1596649283733-1256956795f7?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 2, "favorite": True, "desc": "Seblak dengan topping prasmanan pilihan (mulai 1K)"},
    {"id": 2, "name": "Nasi Penyet Tahu Tempe", "category": "Makanan", "price": 7000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 1, "favorite": False, "desc": "Nasi penyet dengan tahu dan tempe goreng"},
    {"id": 3, "name": "Nasi Penyet Telur", "category": "Makanan", "price": 9000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 1, "favorite": False, "desc": "Nasi penyet dengan telur dadar/ceplok"},
    {"id": 4, "name": "Nasi Penyet 3T (Tahu, Tempe, Telur)", "category": "Makanan", "price": 12000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 2, "favorite": True, "desc": "Nasi penyet komplit tahu, tempe, dan telur"},
    {"id": 5, "name": "Nasi Penyet Ayam", "category": "Makanan", "price": 12000, "image": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 2, "favorite": True, "desc": "Nasi penyet dengan ayam goreng gurih"},
    {"id": 6, "name": "Nasi Penyet Lele", "category": "Makanan", "price": 12000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 2, "favorite": False, "desc": "Nasi penyet dengan lele goreng garing"},
    {"id": 7, "name": "Mie Goreng", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Indomie goreng nikmat"},
    {"id": 8, "name": "Mie Kuah", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Indomie kuah hangat"},
    {"id": 9, "name": "Pop Mie", "category": "Makanan", "price": 8000, "image": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Mie cup praktis"},
    {"id": 10, "name": "Lontong Sambel Tahu", "category": "Makanan", "price": 10000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": "spicy", "spiceLevel": 2, "favorite": False, "desc": "Lontong dengan tahu dan sambal pedas"},
    {"id": 11, "name": "Frozen Food", "category": "Snack", "price": 10000, "image": "https://images.unsplash.com/photo-1528736235302-52922df5c122?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Aneka sosis, nugget goreng"},
    {"id": 12, "name": "Gorengan", "category": "Snack", "price": 1000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Aneka gorengan hangat"},
    {"id": 13, "name": "Kentang Goreng", "category": "Snack", "price": 8000, "image": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": True, "desc": "Kentang goreng renyah"},
    {"id": 14, "name": "Cireng / Sempolan", "category": "Snack", "price": 2000, "image": "https://images.unsplash.com/photo-1626202159047-9759d57a26f3?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Camilan cireng atau sempolan"},
    {"id": 15, "name": "Es Kelapa Muda", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": True, "desc": "Es kelapa muda segar"},
    {"id": 16, "name": "Es Teh Jumbo", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": True, "desc": "Es teh manis porsi jumbo"},
    {"id": 17, "name": "Es Teh Biasa (18 Oz)", "category": "Minuman", "price": 3000, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Es teh manis ukuran reguler"},
    {"id": 18, "name": "Kelapa Muda Utuh + Gula", "category": "Minuman", "price": 10000, "image": "https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Kelapa muda segar disajikan utuh dengan gula"},
    {"id": 19, "name": "Kelapa Muda Utuh + Sirup", "category": "Minuman", "price": 12000, "image": "https://images.unsplash.com/photo-1600718374662-0483d2b9da44?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Kelapa muda segar disajikan utuh dengan sirup"},
    {"id": 20, "name": "Es Buah", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1519996521430-02b798c1d881?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": True, "desc": "Es buah segar pelepas dahaga"},
    {"id": 21, "name": "Es Teh Leci", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Es teh dengan perisa leci segar"},
    {"id": 22, "name": "Es Teh Lemon", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Es teh dengan perasan lemon"},
    {"id": 23, "name": "Es Milk Tea", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1558857563-b371033873b8?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Teh susu nikmat"},
    {"id": 24, "name": "Es Good Day", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Kopi Good Day dingin"},
    {"id": 25, "name": "Es Cappucino", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Cappucino dingin"},
    {"id": 26, "name": "Es Milo", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1542990253-0d0f5be5f0ed?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": True, "desc": "Susu coklat Milo dingin"},
    {"id": 27, "name": "Pop Ice", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1572490122747-3968b75bf699?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Minuman blender rasa buah/susu"},
    {"id": 28, "name": "Es Hilo", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1542990253-0d0f5be5f0ed?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Susu Hilo dingin"},
    {"id": 29, "name": "Kopi Susu", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Kopi dicampur susu"},
    {"id": 30, "name": "White Coffee", "category": "Minuman", "price": 5000, "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Kopi instan Luwak White Koffie"},
    {"id": 31, "name": "Extra Joss", "category": "Minuman", "price": 3000, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Minuman berenergi"},
    {"id": 32, "name": "Extra Joss Susu", "category": "Minuman", "price": 6000, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": True, "desc": "Minuman berenergi campur susu"},
    {"id": 33, "name": "Kopi Hitam", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1550186981-d102bc0f7190?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Kopi hitam panas/dingin"},
    {"id": 34, "name": "Jahe", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1596704017254-9b121068fb31?w=400&h=300&fit=crop", "badge": None, "spiceLevel": 0, "favorite": False, "desc": "Minuman jahe hangat"},
    {"id": 35, "name": "Nutrisari", "category": "Minuman", "price": 4000, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400&h=300&fit=crop", "badge": "ice", "spiceLevel": 0, "favorite": False, "desc": "Minuman segar rasa jeruk/buah lainnya"}
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
    new_order_id = 999
    is_mock = True
    
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
            
            is_mock = False
        except Exception as e:
            print(f"Supabase error: {e}")
            # Fallback to mock ID if insertion fails
            new_order_id = 999
    
    # Integrasi Midtrans Snap jika pembayaran menggunakan QRIS
    snap_token = None
    if order.payment_method == "qris":
        try:
            # Buat permintaan transaksi ke Midtrans
            transaction = {
                "transaction_details": {
                    "order_id": f"ORDER-{new_order_id}-{int(order.total_amount)}",
                    "gross_amount": int(order.total_amount)
                },
                "enabled_payments": ["other_qris"]
            }
            snap_response = snap.create_transaction(transaction)
            snap_token = snap_response['token']
        except Exception as e:
            print(f"Gagal membuat transaksi Midtrans: {e}")
            snap_token = None

    response = {
        "success": True, 
        "order_id": new_order_id,
        "snap_token": snap_token
    }
    
    if is_mock:
        response["warning"] = "Saved to mock (Supabase error or not configured)"
        
    return response

@app.post("/api/webhook/midtrans")
async def midtrans_webhook(request: Request):
    """
    Sensor otomatis dari Midtrans.
    Fungsi ini akan dipanggil oleh server Midtrans setiap kali ada pembaruan status pembayaran.
    """
    try:
        data = await request.json()
        order_id_string = data.get("order_id", "")
        transaction_status = data.get("transaction_status", "")
        
        # Ekstrak ID pesanan asli dari format "ORDER-123-50000"
        order_id = int(order_id_string.split("-")[1])
        
        # Jika transaksi sukses (settlement atau capture)
        if transaction_status in ["settlement", "capture"]:
            if supabase:
                supabase.table("orders").update({"status": "paid"}).eq("id", order_id).execute()
                print(f"Pesanan {order_id} lunas!")
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

# Mount static frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

