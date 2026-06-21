import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, engine, Base
import backend.models as models

def seed_products():
    db = SessionLocal()

    existing = db.query(models.Product).count()
    if existing > 0:
        print(f"Database already has {existing} products. Skipping seed.")
        db.close()
        return

    products = [
        {
            "name": "MacBook Air M3",
            "brand": "Apple",
            "category": "Laptops",
            "description": "The incredibly thin MacBook Air with M3 chip. Up to 18 hours battery life, 8GB RAM, 256GB SSD.",
            "price": 114900,
            "old_price": 129900,
            "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500",
            "stock": 15,
            "rating": 4.8,
            "is_featured": True
        },
        {
            "name": "Dell XPS 15",
            "brand": "Dell",
            "category": "Laptops",
            "description": "Premium 15.6 inch OLED laptop with Intel Core i7, 16GB RAM, 512GB SSD.",
            "price": 149990,
            "old_price": 174990,
            "image_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=500",
            "stock": 10,
            "rating": 4.7,
            "is_featured": True
        },
        {
            "name": "HP Pavilion 15",
            "brand": "HP",
            "category": "Laptops",
            "description": "Everyday laptop with AMD Ryzen 5, 8GB RAM, 512GB SSD. Great value for money.",
            "price": 54990,
            "old_price": 64990,
            "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500",
            "stock": 20,
            "rating": 4.3,
            "is_featured": False
        },
        {
            "name": "Lenovo ThinkPad X1 Carbon",
            "brand": "Lenovo",
            "category": "Laptops",
            "description": "Ultra-light business laptop. Intel Core i7, 16GB RAM, 1TB SSD. Military grade durability.",
            "price": 134990,
            "old_price": None,
            "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500",
            "stock": 8,
            "rating": 4.6,
            "is_featured": False
        },
        {
            "name": "Asus ROG Strix G15",
            "brand": "Asus",
            "category": "Laptops",
            "description": "Gaming powerhouse with AMD Ryzen 9, RTX 4060, 16GB RAM, 1TB SSD. 165Hz display.",
            "price": 124990,
            "old_price": 139990,
            "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500",
            "stock": 12,
            "rating": 4.5,
            "is_featured": True
        },
        {
            "name": "iPhone 15 Pro",
            "brand": "Apple",
            "category": "Phones",
            "description": "The most powerful iPhone ever. A17 Pro chip, titanium design, 48MP camera system, USB-C.",
            "price": 134900,
            "old_price": None,
            "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500",
            "stock": 25,
            "rating": 4.9,
            "is_featured": True
        },
        {
            "name": "Samsung Galaxy S24 Ultra",
            "brand": "Samsung",
            "category": "Phones",
            "description": "200MP camera, built-in S Pen, Snapdragon 8 Gen 3, 12GB RAM, 5000mAh battery.",
            "price": 124999,
            "old_price": 134999,
            "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500",
            "stock": 18,
            "rating": 4.8,
            "is_featured": True
        },
        {
            "name": "OnePlus 12",
            "brand": "OnePlus",
            "category": "Phones",
            "description": "Snapdragon 8 Gen 3, 50MP Hasselblad camera, 100W fast charging, 5400mAh battery.",
            "price": 64999,
            "old_price": 69999,
            "image_url": "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=500",
            "stock": 30,
            "rating": 4.6,
            "is_featured": False
        },
        {
            "name": "Google Pixel 8",
            "brand": "Google",
            "category": "Phones",
            "description": "Google Tensor G3 chip, best-in-class AI features, 50MP camera, 7 years of updates.",
            "price": 75999,
            "old_price": 84999,
            "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500",
            "stock": 15,
            "rating": 4.5,
            "is_featured": False
        },
        {
            "name": "Xiaomi 14 Pro",
            "brand": "Xiaomi",
            "category": "Phones",
            "description": "Leica optics, Snapdragon 8 Gen 3, 50MP triple camera, 120W HyperCharge.",
            "price": 99999,
            "old_price": 109999,
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500",
            "stock": 20,
            "rating": 4.4,
            "is_featured": False
        },
        {
            "name": "iPad Pro M4",
            "brand": "Apple",
            "category": "Tablets",
            "description": "Impossibly thin with M4 chip, Ultra Retina XDR display, Apple Pencil Pro support.",
            "price": 99900,
            "old_price": None,
            "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500",
            "stock": 12,
            "rating": 4.9,
            "is_featured": True
        },
        {
            "name": "Samsung Galaxy Tab S9",
            "brand": "Samsung",
            "category": "Tablets",
            "description": "11 inch Dynamic AMOLED, Snapdragon 8 Gen 2, IP68 water resistant, S Pen included.",
            "price": 74999,
            "old_price": 84999,
            "image_url": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500",
            "stock": 8,
            "rating": 4.6,
            "is_featured": False
        },
        {
            "name": "OnePlus Pad 2",
            "brand": "OnePlus",
            "category": "Tablets",
            "description": "12.1 inch 3K display, Snapdragon 8 Gen 3, 9510mAh battery, 67W fast charging.",
            "price": 49999,
            "old_price": 54999,
            "image_url": "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=500",
            "stock": 15,
            "rating": 4.4,
            "is_featured": False
        },
        {
            "name": "Sony WH-1000XM5",
            "brand": "Sony",
            "category": "Accessories",
            "description": "Industry leading noise cancellation, 30 hour battery, multipoint connection, premium sound.",
            "price": 24990,
            "old_price": 34990,
            "image_url": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500",
            "stock": 35,
            "rating": 4.8,
            "is_featured": True
        },
        {
            "name": "Apple AirPods Pro 2",
            "brand": "Apple",
            "category": "Accessories",
            "description": "Active noise cancellation, Adaptive Audio, H2 chip, MagSafe charging case.",
            "price": 24900,
            "old_price": 26900,
            "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500",
            "stock": 40,
            "rating": 4.7,
            "is_featured": False
        },
        {
            "name": "Samsung Galaxy Watch 6",
            "brand": "Samsung",
            "category": "Accessories",
            "description": "Advanced health monitoring, BioActive sensor, sapphire crystal glass, 40 hour battery.",
            "price": 29999,
            "old_price": 34999,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
            "stock": 22,
            "rating": 4.5,
            "is_featured": False
        },
        {
            "name": "Logitech MX Master 3S",
            "brand": "Logitech",
            "category": "Accessories",
            "description": "8000 DPI sensor, MagSpeed scroll wheel, USB-C charging, works on any surface.",
            "price": 9995,
            "old_price": 12995,
            "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
            "stock": 50,
            "rating": 4.8,
            "is_featured": False
        },
        {
            "name": "Apple Magic Keyboard",
            "brand": "Apple",
            "category": "Accessories",
            "description": "Wireless keyboard with Touch ID, scissor mechanism keys, rechargeable battery.",
            "price": 12900,
            "old_price": None,
            "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500",
            "stock": 28,
            "rating": 4.6,
            "is_featured": False
        },
        {
            "name": "Anker 65W GaN Charger",
            "brand": "Anker",
            "category": "Accessories",
            "description": "Compact 3-port charger, 65W total output, charges laptop and phone simultaneously.",
            "price": 3999,
            "old_price": 4999,
            "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500",
            "stock": 100,
            "rating": 4.7,
            "is_featured": False
        },
        {
            "name": "Samsung 27 inch 4K Monitor",
            "brand": "Samsung",
            "category": "Accessories",
            "description": "27 inch 4K UHD IPS panel, 60Hz, HDR10, USB-C 65W power delivery, slim bezel design.",
            "price": 34990,
            "old_price": 42990,
            "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500",
            "stock": 10,
            "rating": 4.5,
            "is_featured": False
        },
    ]

    for product_data in products:
        product = models.Product(**product_data)
        db.add(product)

    db.commit()
    print(f"Successfully seeded {len(products)} products!")
    db.close()

if __name__ == "__main__":
    seed_products()