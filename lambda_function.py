import json

# File to store products
PRODUCT_FILE = "/tmp/products.json"

def load_products():
    """Load products from the JSON file."""
    try:
        with open(PRODUCT_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_products(products):
    """Save products to the JSON file."""
    with open(PRODUCT_FILE, "w") as f:
        json.dump(products, f)

def lambda_handler(event, context):
    """AWS Lambda handler for CRUD operations."""
    method = event.get("httpMethod")
    body = event.get("body")
    products = load_products()

    if method == "POST":  # Create a product
        product = json.loads(body)
        products.append(product)
        save_products(products)
        return {
            "statusCode": 201,
            "body": json.dumps({"message": "Product added", "product": product}),
        }

    elif method == "GET":  # Get all products
        return {
            "statusCode": 200,
            "body": json.dumps({"products": products}),
        }

    elif method == "PUT":  # Update a product
        product_data = json.loads(body)
        product_id = product_data.get("id")
        for product in products:
            if product["id"] == product_id:
                product.update(product_data)
                save_products(products)
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": "Product updated", "product": product}),
                }
        return {"statusCode": 404, "body": json.dumps({"message": "Product not found"})}

    elif method == "DELETE":  # Delete a product
        product_data = json.loads(body)
        product_id = product_data.get("id")
        products = [p for p in products if p["id"] != product_id]
        save_products(products)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Product deleted", "id": product_id}),
        }

    return {"statusCode": 400, "body": json.dumps({"message": "Invalid request"})}
