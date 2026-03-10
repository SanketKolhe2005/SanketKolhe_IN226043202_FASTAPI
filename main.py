from fastapi import FastAPI, Query
from pydantic import BaseModel, Field  # This line fixes the NameError
from typing import Optional, List

app = FastAPI()
# --- MOCK DATABASE ---
# These items are required to test the logic for Q1, Q2, Q4, and Q5
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]
feedback_db = []

# --- Q1: Filter Products by Min Price ---
@app.get("/products/filter")
def filter_products(
    min_price: Optional[int] = Query(None, description="Minimum price filter"),
    max_price: Optional[int] = Query(None),
    category: Optional[str] = Query(None)
):
    result = products
    if min_price:
        result = [p for p in result if p['price'] >= min_price]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
    if category:
        result = [p for p in result if p['category'].lower() == category.lower()]
    return result

# --- Q2: Get Only Price of a Product ---
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}
    return {"error": "Product not found"}

# --- Q3: Customer Feedback (Pydantic) ---
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback_db.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback_db)
    }

# --- Q4: Product Summary Dashboard ---
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]
    expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }

# --- Q5: Bulk Order Logic ---
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
