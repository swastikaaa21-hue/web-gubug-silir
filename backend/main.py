import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
import midtransclient
import jwt
from datetime import datetime, timedelta, timezone
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

class AdminLogin(BaseModel):
    password: str

class MenuItemCreate(BaseModel):
    name: str
    category: str
    price: float
    description: str = ""
    is_active: bool = True

@app.get("/api/menu")
def get_menu():
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    try:
        response = supabase.table("menu_items").select("*").eq("is_active", True).execute()
        return response.data
    except Exception as e:
        print(f"Supabase error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orders")
def create_order(order: Order):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
        
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
            
    except Exception as e:
        print(f"Supabase error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order in database")
    
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

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-gubugsilir")
security = HTTPBearer()

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=401, detail="Bukan admin")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token kedaluwarsa, silakan login kembali")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token tidak valid")

@app.post("/api/admin/login")
def admin_login(data: AdminLogin):
    if data.password == "ayucitradewi":
        # Buat token expired dalam 24 jam
        exp = datetime.now(timezone.utc) + timedelta(hours=24)
        token = jwt.encode({"role": "admin", "exp": exp}, JWT_SECRET, algorithm="HS256")
        return {"success": True, "token": token}
    raise HTTPException(status_code=401, detail="Sandi salah")

@app.get("/api/admin/menu")
def get_admin_menu(token: dict = Depends(verify_admin_token)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    res = supabase.table("menu_items").select("*").execute()
    return res.data

@app.post("/api/admin/menu")
def create_admin_menu(item: MenuItemCreate, token: dict = Depends(verify_admin_token)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    data = item.dict()
    res = supabase.table("menu_items").insert(data).execute()
    return {"success": True, "data": res.data[0]}

@app.put("/api/admin/menu/{item_id}")
def update_admin_menu(item_id: int, item: MenuItemCreate, token: dict = Depends(verify_admin_token)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    data = item.dict()
    res = supabase.table("menu_items").update(data).eq("id", item_id).execute()
    return {"success": True, "data": res.data[0]}

from datetime import datetime, timedelta, timezone

@app.get("/api/admin/stats")
def get_admin_stats(period: str = "all", token: dict = Depends(verify_admin_token)):
    # period could be: daily, weekly, monthly, all
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    # We fetch all orders for simplicity in this mock, then filter in python
    orders_res = supabase.table("orders").select("*").execute()
    order_items_res = supabase.table("order_items").select("*, menu_items(*)").execute()
    
    orders = orders_res.data
    order_items = order_items_res.data
    
    now = datetime.now(timezone.utc)
    filtered_orders = []
    for o in orders:
        if o["status"] not in ["paid", "pending"]:
            continue
            
        if period == "daily":
            # Check if created_at is today
            created_at = datetime.fromisoformat(o["created_at"].replace('Z', '+00:00'))
            if (now - created_at).days == 0 and now.day == created_at.day:
                filtered_orders.append(o)
        elif period == "weekly":
            # Check if within last 7 days
            created_at = datetime.fromisoformat(o["created_at"].replace('Z', '+00:00'))
            if (now - created_at).days <= 7:
                filtered_orders.append(o)
        elif period == "monthly":
            # Check if within this month
            created_at = datetime.fromisoformat(o["created_at"].replace('Z', '+00:00'))
            if now.year == created_at.year and now.month == created_at.month:
                filtered_orders.append(o)
        else:
            filtered_orders.append(o)
            
    filtered_order_ids = {o["id"] for o in filtered_orders}
    
    # Calculate stats
    total_revenue = sum(float(o["total_amount"]) for o in filtered_orders)
    
    # Filter order items that belong to the filtered orders
    filtered_order_items = [oi for oi in order_items if oi["order_id"] in filtered_order_ids]
    
    items_sold_count = sum(oi["quantity"] for oi in filtered_order_items)
    
    # Top items by category
    sales_by_item = {}
    for oi in filtered_order_items:
        if not oi.get("menu_items"): continue
        cat = oi["menu_items"]["category"]
        name = oi["menu_items"]["name"]
        key = f"{cat}::{name}"
        if key not in sales_by_item:
            sales_by_item[key] = 0
        sales_by_item[key] += oi["quantity"]
        
    top_items = [{"category": k.split("::")[0], "name": k.split("::")[1], "sold": v} for k, v in sales_by_item.items()]
    top_items.sort(key=lambda x: x["sold"], reverse=True)
    
    return {
        "total_revenue": total_revenue,
        "total_items_sold": items_sold_count,
        "top_items": top_items[:10]
    }

# Mount static frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "asset")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/asset", StaticFiles(directory=ASSET_DIR), name="asset")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

