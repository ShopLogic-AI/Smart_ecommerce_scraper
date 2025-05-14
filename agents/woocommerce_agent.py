# agents/woocommerce_agent.py
from woocommerce import API

class WooCommerceAgent:
    def __init__(self, url, consumer_key, consumer_secret):
        self.wcapi = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3"
        )

    def extract_products(self):
        products = self.wcapi.get("products").json()
        return [
            {
                "title": p["name"],
                "description": p["description"],
                "available": p["stock_status"] == "instock",
                "vendor": p.get("vendor", "N/A"),
                "category": p["categories"][0]["name"] if p["categories"] else "N/A",
                "price": p["price"]
            }
            for p in products
        ]
