import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Toy, Order

app = FastAPI(title="Toy Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Toy Store Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the Toy Store API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    return response

# ----- Toy Endpoints -----

@app.get("/api/toys")
def list_toys(category: Optional[str] = None, q: Optional[str] = None):
    """List toys with optional category filter and search query"""
    if db is None:
        return []
    filter_dict = {}
    if category:
        filter_dict["category"] = category
    if q:
        filter_dict["name"] = {"$regex": q, "$options": "i"}
    toys = get_documents("toy", filter_dict=filter_dict, limit=100)
    for t in toys:
        t["_id"] = str(t.get("_id"))
    return toys

class CreateToy(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image: Optional[str] = None
    rating: Optional[float] = 4.5
    in_stock: bool = True

@app.post("/api/toys", status_code=201)
def create_toy(payload: CreateToy):
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    toy = Toy(**payload.model_dump())
    inserted_id = create_document("toy", toy)
    return {"_id": inserted_id}

@app.get("/api/toys/{toy_id}")
def get_toy(toy_id: str):
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        obj_id = ObjectId(toy_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid toy id")
    doc = db["toy"].find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Toy not found")
    doc["_id"] = str(doc["_id"])
    return doc

# ----- Order Endpoints -----

class CreateOrder(BaseModel):
    customer_name: str
    customer_email: str
    customer_address: str
    items: List[dict]
    subtotal: float
    shipping: float = 0
    total: float
    notes: Optional[str] = None

@app.post("/api/orders", status_code=201)
def create_order(payload: CreateOrder):
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    # Basic validation: ensure items present
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")
    order = Order(**payload.model_dump())
    order_id = create_document("order", order)
    return {"order_id": order_id}

@app.get("/api/seed", tags=["dev"]) 
def seed_sample_toys():
    """Seed database with a few sample toys if empty"""
    if db is None:
        return {"status": "Database unavailable"}
    count = db["toy"].count_documents({})
    if count > 0:
        return {"status": "already-seeded", "count": count}
    samples = [
        {
            "name": "Cuddly Bear",
            "description": "Super soft plush bear.",
            "price": 19.99,
            "category": "Plush",
            "image": "https://images.unsplash.com/photo-1612198185720-2d3a9c5a4f8e",
            "rating": 4.7,
            "in_stock": True,
        },
        {
            "name": "Rainbow Stacking Rings",
            "description": "Classic stacking rings for toddlers.",
            "price": 14.99,
            "category": "Educational",
            "image": "https://images.unsplash.com/photo-1582582621959-48f5f1d7fca1",
            "rating": 4.6,
            "in_stock": True,
        },
        {
            "name": "STEM Robot Kit",
            "description": "Build and program your own robot.",
            "price": 49.99,
            "category": "STEM",
            "image": "https://images.unsplash.com/photo-1581090464777-f3220bbe1b8b",
            "rating": 4.8,
            "in_stock": True,
        },
    ]
    inserted = 0
    for s in samples:
        try:
            create_document("toy", s)
            inserted += 1
        except Exception:
            pass
    return {"status": "seeded", "inserted": inserted}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
