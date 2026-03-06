from sqlalchemy.orm import Session
from app.models.item import Item


INITIAL_ITEMS = [
    {
        "name": "Wireless Bluetooth Headphones",
        "description": "High-quality over-ear wireless headphones with noise cancellation and 30-hour battery life.",
        "price": 79.99,
        "stock": 50,
        "category": "Electronics",
    },
    {
        "name": "Stainless Steel Water Bottle",
        "description": "Double-walled insulated water bottle, keeps drinks cold for 24h or hot for 12h. 750ml capacity.",
        "price": 24.99,
        "stock": 100,
        "category": "Kitchen",
    },
    {
        "name": "Running Shoes - Sport Pro",
        "description": "Lightweight running shoes with cushioned sole and breathable mesh upper.",
        "price": 119.99,
        "stock": 30,
        "category": "Sports",
    },
    {
        "name": "Organic Green Tea Pack",
        "description": "Premium organic green tea, 100 tea bags. Rich in antioxidants.",
        "price": 15.99,
        "stock": 200,
        "category": "Food & Beverages",
    },
    {
        "name": "USB-C Fast Charger",
        "description": "65W USB-C fast charger compatible with laptops, tablets, and smartphones.",
        "price": 34.99,
        "stock": 75,
        "category": "Electronics",
    },
    {
        "name": "Yoga Mat - Premium",
        "description": "Non-slip yoga mat, 6mm thick, eco-friendly material. Includes carrying strap.",
        "price": 39.99,
        "stock": 60,
        "category": "Sports",
    },
    {
        "name": "Sunglasses - UV Protection",
        "description": "Polarized sunglasses with UV400 protection. Stylish aviator design.",
        "price": 49.99,
        "stock": 45,
        "category": "Accessories",
    },
    {
        "name": "Wooden Desk Organizer",
        "description": "Handcrafted wooden desk organizer with multiple compartments for pens, cards, and accessories.",
        "price": 29.99,
        "stock": 40,
        "category": "Office",
    },
    {
        "name": "Basketball - Official Size",
        "description": "Official size 7 basketball, indoor/outdoor use. Durable composite leather.",
        "price": 29.99,
        "stock": 35,
        "category": "Sports",
    },
    {
        "name": "LED Desk Lamp",
        "description": "Adjustable LED desk lamp with 5 brightness levels and 3 color temperatures. USB charging port.",
        "price": 44.99,
        "stock": 55,
        "category": "Home",
    },
    {
        "name": "Portable Bluetooth Speaker",
        "description": "Waterproof portable speaker with 12-hour battery life and deep bass.",
        "price": 59.99,
        "stock": 40,
        "category": "Electronics",
    },
    {
        "name": "Cotton T-Shirt - Classic Fit",
        "description": "100% organic cotton t-shirt, available in multiple colors. Comfortable classic fit.",
        "price": 19.99,
        "stock": 150,
        "category": "Clothing",
    },
    {
        "name": "Coffee Table Book - World Photography",
        "description": "Stunning collection of world photography. 300 pages, hardcover.",
        "price": 45.99,
        "stock": 25,
        "category": "Books",
    },
    {
        "name": "Smart Watch - Fitness Tracker",
        "description": "Smart watch with heart rate monitor, GPS, sleep tracking, and 7-day battery life.",
        "price": 149.99,
        "stock": 20,
        "category": "Electronics",
    },
    {
        "name": "Ceramic Coffee Mug Set",
        "description": "Set of 4 handmade ceramic coffee mugs, 350ml each. Microwave and dishwasher safe.",
        "price": 34.99,
        "stock": 80,
        "category": "Kitchen",
    },
]


def seed_items(db: Session):
    """Seed the database with initial items if the items table is empty."""
    existing_count = db.query(Item).count()
    if existing_count > 0:
        return

    for item_data in INITIAL_ITEMS:
        item = Item(**item_data)
        db.add(item)

    db.commit()
    print(f"Seeded {len(INITIAL_ITEMS)} items into the database.")
