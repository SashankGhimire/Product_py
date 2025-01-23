from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import dotenv_values


config = dotenv_values(".env")

app = Flask(__name__)

# Database connection parameters
DB_USERNAME = config['DB_USERNAME']
DB_PASSWORD = config['DB_PASSWORD']
DB_HOST = config['DB_HOST']
DB_PORT = config['DB_PORT']
DB_NAME = config['DB_NAME']        

# Configure MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)

# Route to add a product
@app.route('/add-product', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        price=data['price'],
        category=data['category']
    )
    db.session.add(new_product)
    db.session.commit() #To save Changes
    return jsonify({'message': 'Product added successfully'}), 201

# Route to list all products
@app.route('/list-product', methods=['GET'])
def list_product():
    products = Product.query.all()
    return jsonify([{ 'id': p.id, 'name': p.name, 'price': p.price, 'category': p.category } for p in products])

# Route to remove a product by ID
@app.route('/remove-product/<int:id>', methods=['DELETE'])
def remove_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product removed successfully'})
    return jsonify({'message': 'Product not found'}), 404

# Route to update a product by ID
@app.route('/update-product/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if product:
        data = request.get_json()
        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.category = data.get('category', product.category)
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'})
    return jsonify({'message': 'Product not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)