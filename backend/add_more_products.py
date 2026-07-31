import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal
import backend.models as models


def add_more_products():
    db = SessionLocal()

    products = [

        # ---------------- AUDIO ----------------

        {
            "name": "Sennheiser Momentum 4 Wireless",
            "brand": "Sennheiser",
            "category": "Audio",
            "description": "Premium wireless headphones with adaptive noise cancellation and 60 hour battery life.",
            "price": 27990,
            "old_price": 32990,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
            "stock": 20,
            "rating": 4.7,
            "is_featured": False
        },

        {
            "name": "Marshall Stanmore III Speaker",
            "brand": "Marshall",
            "category": "Audio",
            "description": "Classic Marshall design Bluetooth speaker with powerful stereo sound.",
            "price": 41999,
            "old_price": 45999,
            "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500",
            "stock": 12,
            "rating": 4.6,
            "is_featured": True
        },

        {
            "name": "Jabra Elite 10 Earbuds",
            "brand": "Jabra",
            "category": "Audio",
            "description": "Wireless earbuds with Dolby Atmos, ANC and premium calling experience.",
            "price": 14999,
            "old_price": 17999,
            "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500",
            "stock": 30,
            "rating": 4.5,
            "is_featured": False
        },

        {
            "name": "Beats Studio Pro",
            "brand": "Beats",
            "category": "Audio",
            "description": "Over-ear headphones with active noise cancellation and Apple ecosystem support.",
            "price": 34900,
            "old_price": 39900,
            "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500",
            "stock": 16,
            "rating": 4.6,
            "is_featured": False
        },

        {
            "name": "Bose SoundLink Flex",
            "brand": "Bose",
            "category": "Audio",
            "description": "Portable waterproof Bluetooth speaker with premium balanced sound.",
            "price": 15990,
            "old_price": 18990,
            "image_url": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=500",
            "stock": 25,
            "rating": 4.5,
            "is_featured": False
        },


        # ---------------- DISPLAYS ----------------

        {
            "name": "BenQ PD2705U 4K Monitor",
            "brand": "BenQ",
            "category": "Displays",
            "description": "Professional 27 inch 4K monitor designed for creators and designers.",
            "price": 44999,
            "old_price": 49999,
            "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500",
            "stock": 10,
            "rating": 4.7,
            "is_featured": True
        },

        {
            "name": "ASUS TUF Gaming 27 Monitor",
            "brand": "Asus",
            "category": "Displays",
            "description": "Gaming monitor with high refresh rate, adaptive sync and fast response time.",
            "price": 26999,
            "old_price": 31999,
            "image_url": "https://images.unsplash.com/photo-1547119957-637f8679db1e?w=500",
            "stock": 18,
            "rating": 4.5,
            "is_featured": False
        },

        {
            "name": "Acer Nitro VG240Y Monitor",
            "brand": "Acer",
            "category": "Displays",
            "description": "Affordable gaming display with Full HD resolution and smooth refresh rate.",
            "price": 13999,
            "old_price": 16999,
            "image_url": "https://images.unsplash.com/photo-1551645120-d70bfe84c826?w=500",
            "stock": 22,
            "rating": 4.4,
            "is_featured": False
        },


        # ---------------- ACCESSORIES ----------------

        {
            "name": "Razer DeathAdder V3 Mouse",
            "brand": "Razer",
            "category": "Accessories",
            "description": "Professional gaming mouse with ergonomic design and high precision sensor.",
            "price": 6999,
            "old_price": 8999,
            "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=500",
            "stock": 40,
            "rating": 4.7,
            "is_featured": True
        },

        {
            "name": "SanDisk Extreme Portable SSD 1TB",
            "brand": "SanDisk",
            "category": "Accessories",
            "description": "Fast portable SSD with USB-C connectivity and rugged protection.",
            "price": 8999,
            "old_price": 10999,
            "image_url": "https://images.unsplash.com/photo-1597872250969-1c2f7d8f1b8f?w=500",
            "stock": 35,
            "rating": 4.6,
            "is_featured": False
        }
    ]


    for product_data in products:
        product = models.Product(**product_data)
        db.add(product)

    db.commit()

    print(f"Successfully added {len(products)} new products")

    db.close()


if __name__ == "__main__":
    add_more_products()