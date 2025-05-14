# agents/shopify_agent.py
import requests

class ShopifyAgent:
    def __init__(self, store_url, access_token):
        self.store_url = store_url
        self.headers = {
            "X-Shopify-Storefront-Access-Token": access_token,
            "Content-Type": "application/json"
        }

    def extract_products(self):
        query = """
        {
          products(first: 10) {
            edges {
              node {
                title
                description
                availableForSale
                vendor
                productType
                variants(first: 1) {
                  edges {
                    node {
                      price {
                        amount
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        response = requests.post(self.store_url, headers=self.headers, json={"query": query})
        data = response.json()
        return [
            {
                "title": p["node"]["title"],
                "description": p["node"]["description"],
                "available": p["node"]["availableForSale"],
                "vendor": p["node"]["vendor"],
                "category": p["node"]["productType"],
                "price": p["node"]["variants"]["edges"][0]["node"]["price"]["amount"]
            }
            for p in data["data"]["products"]["edges"]
        ]
