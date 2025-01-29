from pymongo import MongoClient

# MongoDB Configuration (Using MongoDB Atlas)
MONGO_URI = "mongodb+srv://mongo:mongo@AWSLambda.7tpcj.mongodb.net/?retryWrites=true&w=majority&appName=AWSLambda"
DB_NAME = "CRUD"
COLLECTION_NAME = "Products"
#counter_collection is intended to control and track the sequence of product ID, 
#both uniquely and consistently. In MongoDB, an _id field gets created for 
#each document, but it usually defaults to an ObjectId-an identifier of 12 bytes 
#that is generated automatically. 
COUNTER_COLLECTION = "Counters"  # Collection for tracking the ID

# Initialize MongoDB client globally (to be reused across Lambda invocations)
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
counter_collection = db[COUNTER_COLLECTION]  # Counter collection

# Lambda handler function
def lambda_handler(event, context):
    action = event.get("action")
    data = event.get("data")

    # Validation function
    def validate_product(product):
        if "name" not in product or not isinstance(product["name"], str) or not product["name"].strip():
            return "Product name is required and must be a non-empty string."
        if "price" not in product or not isinstance(product["price"], (int, float)) or product["price"] < 0:
            return "Price is required and must be a non-negative number."
        if "category" not in product or not isinstance(product["category"], str) or not product["category"].strip():
            return "Category is required and must be a non-empty string."
        return None

    try:
        # Get the next available product ID from the counter collection
        def get_next_product_id():
            # searches for the document with _id = "product_id"
            counter_doc = counter_collection.find_one_and_update(
                {"_id": "product_id"},  
                {"$inc": {"sequence_value": 1}},  # Increment the counter
                upsert=True,  # if it doesn't exist
                return_document=True
            )
            # Return the updated sequence_value
            return counter_doc["sequence_value"]

        # Add a product
        if action == "add":
            if not data:
                return {"status": "error", "message": "Product data is required to add a product"}
            validation_error = validate_product(data)
            if validation_error:
                return {"status": "error", "message": validation_error}

            # Get the next available _id from the counter collection
            next_id = get_next_product_id()

            data["_id"] = next_id  # Assign the new product ID as an integer
            result = collection.insert_one(data)

            return {"status": "success", "product": data}

        # Update a product
        elif action == "update":
            if not data or "id" not in data:
                return {"status": "error", "message": "Product ID and data are required for update"}

            # Extract the product ID from the data
            product_id = data.pop("id")  # Remove 'id' from the update data

            # Ensure the ID is in the correct format (it should be an integer in this case)
            if not isinstance(product_id, int):
                return {"status": "error", "message": "Product ID must be an integer."}

            # Validate the product data
            validation_error = validate_product(data)
            if validation_error:
                return {"status": "error", "message": validation_error}

            # Perform the update operation
            result = collection.update_one({"_id": product_id}, {"$set": data})

            if result.matched_count == 0:
                return {"status": "error", "message": f"Product with ID {product_id} does not exist"}
            
            # Fetch the updated product to return the complete information
            updated_product = collection.find_one({"_id": product_id}, {"_id": 1, "name": 1, "price": 1, "category": 1})

            # Convert ObjectId to string for serialization
            updated_product["_id"] = str(updated_product["_id"])

            return {"status": "success", "product": updated_product}

        # Delete a product
        elif action == "delete":
            if not data or "id" not in data:
                return {"status": "error", "message": "Product ID is required for delete"}

            product_id = data["id"]

            result = collection.delete_one({"_id": product_id})
            if result.deleted_count == 0:
                return {"status": "error", "message": f"Product with ID {product_id} does not exist"}
            return {"status": "success", "deleted": True}

        # List all products
        elif action == "list":
            products = list(collection.find({}, {"_id": 1, "name": 1, "price": 1, "category": 1}))  # Include _id
            if not products:
                return {"status": "error", "message": "No products found"}

            # Convert ObjectId to string for serialization
            for product in products:
                product["_id"] = str(product["_id"])  # Convert ObjectId to string

            return {"status": "success", "products": products}

        # List products by category
        elif action == "list_by_category":
            if not data or "category" not in data:
                return {"status": "error", "message": "Category is required to filter products"}

            filtered_products = list(collection.find({"category": data["category"]}, {"_id": 1, "name": 1, "price": 1, "category": 1}))
            if not filtered_products:
                return {"status": "error", "message": f"No products found in category '{data['category']}'"}
            return {"status": "success", "products": filtered_products}

        else:
            return {"status": "error", "message": "Invalid action"}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}
