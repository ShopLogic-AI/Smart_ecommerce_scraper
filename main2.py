# main.py
from agents.shopify_agent import ShopifyAgent
from agents.woocommerce_agent import WooCommerceAgent
from utils.storage import save_to_json

def run_shopify():
    shopify_agent = ShopifyAgent(
        store_url="https://rowingblazers.com/collections/shop-all/api/2023-04/graphql.json",
        access_token="2a1753b19c85ac630f27391da802765d"
    )
    data = shopify_agent.extract_products()
    save_to_json(data, "data/shopify_output.json")

def run_woocommerce():
    woo_agent = WooCommerceAgent(
        url="https://your-woocommerce-site.com",
        consumer_key="your_consumer_key",
        consumer_secret="your_consumer_secret"
    )
    data = woo_agent.extract_products()
    save_to_json(data, "data/woocommerce_output.json")

if __name__ == "__main__":
    run_shopify()
    run_woocommerce()
