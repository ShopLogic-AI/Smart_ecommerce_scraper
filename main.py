import requests
import json
import time
import logging
from urllib.parse import urlparse, urlunparse
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def clean_datetime(dt_string):
    if not dt_string:
        return None
    try:
        return datetime.fromisoformat(dt_string.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return None


# --- Configuration ---
STORE_DOMAINS = [
    "allbirds.com",
]

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ecommerce_data',
}

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def construct_url(domain):
    parsed = urlparse(f"//{domain}")
    scheme = "https"
    netloc = parsed.netloc or parsed.path
    return urlunparse((scheme, netloc, "/products.json", "", "", ""))

def fetch_products(url):
    products = []
    page = 1
    limit = 250
    while True:
        paginated_url = f"{url}?limit={limit}&page={page}"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(paginated_url, timeout=30, headers=headers)
            response.raise_for_status()
            data = response.json()
            if "products" in data and data["products"]:
                products.extend(data["products"])
                if len(data["products"]) < limit:
                    break
                page += 1
            else:
                break
            time.sleep(1.5)
        except Exception as e:
            logging.error(f"Error fetching data from {paginated_url}: {e}")
            break
    return products

def flatten_data(all_products_data, store_domain):
    flattened_rows = []
    for product in all_products_data:
        product_id = product.get('id')
        first_image_src = product.get('images', [{}])[0].get('src') if product.get('images') else None
        all_image_srcs = '|'.join([img.get('src', '') for img in product.get('images', []) if img.get('src')])
        if not product.get('variants'):
            row = {
                'store_domain': store_domain,
                'product_id': product_id,
                'title': product.get('title'),
                'handle': product.get('handle'),
                'vendor': product.get('vendor'),
                'product_type': product.get('product_type'),
                'created_at': clean_datetime(product.get('created_at')),
                'updated_at': clean_datetime(product.get('updated_at')),
                'published_at': clean_datetime(product.get('published_at')),
                'tags': ', '.join(product.get('tags', [])),
                'body_html': product.get('body_html'),
                'variant_id': None,
                'variant_title': None,
                'sku': None,
                'price': None,
                'compare_at_price': None,
                'available': None,
                'variant_created_at': None,
                'variant_updated_at': None,
                'image_src': first_image_src,
                'all_image_srcs': all_image_srcs,
            }
            flattened_rows.append(row)
        else:
            for variant in product.get('variants', []):
                row = {
                    'store_domain': store_domain,
                    'product_id': product_id,
                    'title': product.get('title'),
                    'handle': product.get('handle'),
                    'vendor': product.get('vendor'),
                    'product_type': product.get('product_type'),
                    'created_at': clean_datetime(product.get('created_at')),
                    'updated_at': clean_datetime(product.get('updated_at')),
                    'published_at': clean_datetime(product.get('published_at')),
                    'tags': ', '.join(product.get('tags', [])),
                    'body_html': product.get('body_html'),
                    'variant_id': variant.get('id'),
                    'variant_title': variant.get('title'),
                    'sku': variant.get('sku'),
                    'price': variant.get('price'),
                    'compare_at_price': variant.get('compare_at_price'),
                    'available': variant.get('available'),
                    'variant_created_at': clean_datetime(variant.get('created_at')),
                    'variant_updated_at': clean_datetime(variant.get('updated_at')),
                    'image_src': first_image_src,
                    'all_image_srcs': all_image_srcs,
                }
                flattened_rows.append(row)
    return flattened_rows

def save_to_mysql(data, db_config):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO shopify_products (
                store_domain, product_id, title, handle, vendor, product_type,
                created_at, updated_at, published_at, tags, body_html,
                variant_id, variant_title, sku, price, compare_at_price,
                available, variant_created_at, variant_updated_at,
                image_src, all_image_srcs
            ) VALUES (
                %(store_domain)s, %(product_id)s, %(title)s, %(handle)s, %(vendor)s, %(product_type)s,
                %(created_at)s, %(updated_at)s, %(published_at)s, %(tags)s, %(body_html)s,
                %(variant_id)s, %(variant_title)s, %(sku)s, %(price)s, %(compare_at_price)s,
                %(available)s, %(variant_created_at)s, %(variant_updated_at)s,
                %(image_src)s, %(all_image_srcs)s
            )
        """
        cursor.executemany(query, data)
        conn.commit()
        logging.info(f"Inserted {cursor.rowcount} rows into MySQL.")
    except Error as e:
        logging.error(f"MySQL error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Run the Script ---
if __name__ == "__main__":
    for domain in STORE_DOMAINS:
        logging.info(f"--- Scraping {domain} ---")
        url = construct_url(domain)
        if not url:
            continue
        products = fetch_products(url)
        if products:
            flattened = flatten_data(products, domain)
            if flattened:
                save_to_mysql(flattened, DB_CONFIG)
            else:
                logging.warning(f"No flattened data for {domain}.")
        else:
            logging.warning(f"No products fetched for {domain}.")
        time.sleep(2)
    logging.info("✅ All done.")
