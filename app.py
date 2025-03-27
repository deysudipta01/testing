from flask import Flask, render_template, request, redirect, url_for, jsonify,session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId  # Import ObjectId
import bcrypt
from datetime import datetime
import random
import string
from flask import render_template, request, redirect, url_for, session
import pymongo
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from bson import ObjectId




app = Flask(__name__)

# MongoDB Atlas Connection URI
app.config["MONGO_URI"] = "mongodb+srv://riju:Sudiptadey123@cluster0.kpda0.mongodb.net/ecommerce_db"
mongo = PyMongo(app)

# MongoDB Collections
users = mongo.db.users
products = mongo.db.products
admin = mongo.db.admin

app.secret_key = 'your_secret_key'
app.config['SESSION_COOKIE_SECURE'] = True  # Use HTTPS for session cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookies


# ✅ Define upload folder and allowed extensions
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ✅ Check if the uploaded file is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Home page
@app.route('/')
def home():
    return render_template('home.html')



# Adminlogin page
@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')



# ✅ adminLogin Endpoint
@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        # Fetch user from MongoDB
        admin_user = admin.find_one({'phone': phone})

        # Compare entered password with stored password
        if admin_user and password == admin_user['password']:
            session['phone'] = phone  # Store phone number in session
            return render_template('admin.html')
        else:
            return 'Invalid credentials!'
    return render_template('adminlogin.html')  # Render the login page for GET request

# ✅ Admin Logout2 Route
@app.route('/logout2')
def logout2():
    session.clear()  # Clear session data
    return redirect(url_for('home'))  # Redirect to home page




# ✅ Fetch All Products (API)
@app.route('/api/products', methods=['GET'])
def get_products():
    all_products = list(products.find())
    for product in all_products:
        product['_id'] = str(product['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(all_products)

# ✅ Add New Product (API)
@app.route('/api/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form['description']

    # Handle image upload
    image_path = 'static/images/default.jpg'  # Default image if no file is uploaded
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

    # ✅ Insert product into MongoDB
    product_data = {
        'name': name,
        'price': price,
        'description': description,
        'image': image_path
    }
    products.insert_one(product_data)
    return jsonify({'success': True})


# ✅ Update Existing Product (API)
@app.route('/api/update_product/<product_id>', methods=['PUT'])
def update_product(product_id):
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form['description']

    # Get existing product to retain old image if new one is not provided
    product = products.find_one({'_id': ObjectId(product_id)})
    image_path = product['image'] if product else 'static/images/default.jpg'

    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

    # ✅ Update product in MongoDB
    products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': {
            'name': name,
            'price': price,
            'description': description,
            'image': image_path
        }}
    )
    return jsonify({'success': True})


# ✅ Delete Product (API)
@app.route('/api/delete_product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    products.delete_one({'_id': ObjectId(product_id)})
    return jsonify({'success': True})


# Get all orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = list(mongo.db.orders.find({}))
    for order in orders:
        order['_id'] = str(order['_id'])
    return jsonify(orders)


# Update order status
@app.route('/api/update_order/<order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.json
    status = data.get('status')

    if not status:
        return jsonify({"error": "Status is required"}), 400

    mongo.db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': status}})
    return jsonify({"message": "Order status updated successfully!"})


# Delete an order
@app.route('/api/delete_order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    mongo.db.orders.delete_one({'_id': ObjectId(order_id)})
    return jsonify({"message": "Order deleted successfully!"})






#✅start user login here indexpage==userlogin page


@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname=request.form['fullname']
        phone = request.form['phone']
        password = request.form['password']

        # Check if the user already exists
        if users.find_one({'phone': phone}):
            return 'User already exists!'

        # Insert new user into MongoDB
        users.insert_one({'fullname':fullname,'phone': phone, 'password': password})
        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('register.html')  # Render the registration page for GET request



# ✅ Login Endpoint
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        # Fetch user from MongoDB
        user = users.find_one({'phone': phone})

        # Compare entered password with stored password
        if user and password == user['password']:
            session['phone'] = phone  # Store phone number in session
            return redirect(url_for('products_page'))
        else:
            return 'Invalid credentials!'
    return render_template('index.html')  # Render the login page for GET request


# --------------------------------
# ✅ Logout Route
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('index'))  # Redirect to homepage after logout










@app.route('/products')
def products_page():
    phone = session.get('phone')  # ✅ Get phone securely from session
    if not phone:
        return redirect(url_for('login'))  # Redirect if no session
    # Fetch all products from MongoDB
    all_products = list(products.find())

    # Fetch user's cart from MongoDB
    user = users.find_one({'phone': phone})
    cart = user.get('cart', []) if user else []  # Get cart if user exists

    return render_template('products.html', products=all_products,  cart=cart)


# Route to display product details
@app.route('/product/<product_id>')
def product_details(product_id):
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    # Fetch all products for the related product section
    all_products = list(mongo.db.products.find())

    if not product:
        return "Product not found", 404

    return render_template('product_details.html', product=product,products=all_products)



@app.route('/get_cart', methods=['GET'])
def get_cart():
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})
    # Fetch the user's cart from the database
    user = users.find_one({'phone': phone})
    cart = user.get('cart', []) if user else []

    return jsonify({'cart': cart})



@app.route('/reduce_from_cart', methods=['POST'])
def reduce_from_cart():
    data = request.json
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})

    product_id = data['productId']

    # Ensure productId is an ObjectId
    try:
        product_id = ObjectId(product_id)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid product ID: {str(e)}'})

    # Fetch user from MongoDB
    user = users.find_one({'phone': phone})

    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    # Fetch the product from the MongoDB products collection
    product = products.find_one({'_id': product_id})

    if not product:
        return jsonify({'success': False, 'message': 'Product not found!'})

    # Get the cart and update the quantity of the item
    cart = user.get('cart', [])
    product_found = False
    for item in cart:
        if item['productId'] == str(product['_id']):
            if item['quantity'] > 1:
                item['quantity'] -= 1  # Decrease the quantity by 1
            else:
                cart.remove(item)  # Remove the product if quantity is 1
            product_found = True
            break

    if not product_found:
        return jsonify({'success': False, 'message': 'Product not found in cart!'})

    # Update the user's cart in MongoDB
    result = users.update_one({'phone': phone}, {'$set': {'cart': cart}})

    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Product quantity reduced!'})
    else:
        return jsonify({'success': False, 'message': 'Error updating cart.'})


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})
    product_id = data['productId']

    try:
        product_id = ObjectId(product_id)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid product ID: {str(e)}'})

    user = users.find_one({'phone': phone})
    product = products.find_one({'_id': product_id})

    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    if not product:
        return jsonify({'success': False, 'message': 'Product not found!'})

    cart = user.get('cart', [])
    product_found = False
    for item in cart:
        if item['productId'] == str(product['_id']):
            item['quantity'] += 1
            product_found = True
            break

    if not product_found:
        cart.append({
            'productId': str(product['_id']),
            'name': product['name'],
            'price': product['price'],
            'quantity': 1,
            'image': product['image']  # Add image path here

        })

    # Log the cart before saving it to MongoDB
    print(f"Cart after adding product: {cart}")

    result = users.update_one({'phone': phone}, {'$set': {'cart': cart}})
    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Product added to cart!'})
    else:
        return jsonify({'success': False, 'message': 'Error updating cart.'})


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})
    product_id = data['productId']

    # Ensure productId is an ObjectId
    try:
        product_id = ObjectId(product_id)  # Convert the productId to ObjectId
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid product ID: {str(e)}'})

    # Fetch user from MongoDB
    user = users.find_one({'phone': phone})

    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    # Find the product in the cart and remove it
    cart = user.get('cart', [])
    updated_cart = [item for item in cart if item['productId'] != str(product_id)]

    # Update the user's cart in MongoDB
    result = users.update_one({'phone': phone}, {'$set': {'cart': updated_cart}})

    if result.modified_count > 0:
        return jsonify({'success': True, 'message': 'Product removed from cart!'})
    else:
        return jsonify({'success': False, 'message': 'Error updating cart.'})


def get_cart_by_phone(phone):
    user = users.find_one({'phone': phone})
    if user:
        cart = user.get('cart', [])
        print(f"User {phone} cart: {cart}")  # Log the cart contents for debugging
        return cart
    else:
        print(f"User {phone} not found")  # Log if user is not found
        return []




@app.route('/checkout')
def checkout():
    phone = session.get('phone')
    if not phone:
        return redirect(url_for('login'))

    cart = get_cart_by_phone(phone)
    if not cart:
        print(f"Cart is empty for user {phone}")
        return "Error: Cart is empty"

    total_price = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price)



# Fetch user details by phone
@app.route('/get_user_details')
def get_user_details():
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})

    user = users.find_one({'phone': phone})
    if user:
        return jsonify({'success': True, 'user': {'fullname': user['fullname'], 'phone': user['phone']}})
    else:
        return jsonify({'success': False, 'message': 'User not found'})

# Fetch order history by phone
@app.route('/get_order_history')
def get_order_history():
    phone = session.get('phone')
    if not phone:
        return jsonify({'success': False, 'message': 'Unauthorized access!'})
    order_history = list(orders.find({'phone': phone}))
    if order_history:
        for order in order_history:
            order['_id'] = str(order['_id'])  # Convert ObjectId to string
            for item in order['items']:
                item['item_id'] = str(item['item_id'])
        return jsonify({'success': True, 'orders': order_history})
    else:
        return jsonify({'success': False, 'message': 'No orders found'})




@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    phone = session.get('phone')  # Get phone number from session, this is the user's actual phone number

    if not phone:
        return redirect(url_for('login'))  # If no phone in session, redirect to login

    # Fetch the cart data for the user using the actual phone number
    cart = get_cart_by_phone(phone)

    if not cart:
        return redirect(url_for('products_page', phone=phone))  # If the cart is empty, go back to the products page

    # Calculate total price for the cart
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    delivery_charge = 50.00  # ₹50 fixed delivery fee
    discount = subtotal * 0.1  # 10% discount on subtotal
    total_price= subtotal + delivery_charge - discount

    if request.method == 'POST':
        # Get the shipping details from the form
        name = request.form['name']
        phno = request.form['phno']
        shipping_phone = request.form['phone']  # This is the phone number for delivery
        address = request.form['address']
        payment_method = request.form['payment_method']

        # Store the user's details in the session
        session['shipping_details'] = {
            'name': name,
            'phno':phno,
            'phone': shipping_phone,  # Store the delivery phone number
            'address': address,
            'payment_method': payment_method,
            'total_price': total_price
        }

        if payment_method == 'cod':
            # Generate a random 4-digit code
            confirmation_code = ''.join(random.choices(string.digits, k=4))
            session['confirmation_code'] = confirmation_code  # Store the code in the session

            # Redirect to the confirmation page with the generated code
            return redirect(url_for('cod_confirmation'))
        else:
            # For online payment, redirect to the online payment page
            return redirect(url_for('online_payment', phone=phone, total_price=total_price))

    return render_template('shipping.html', cart=cart, total_price=total_price)


@app.route('/cod_confirmation')
def cod_confirmation():
    # Retrieve the confirmation code from the session
    confirmation_code = session.get('confirmation_code')

    # Render the confirmation page with the confirmation code
    return render_template('cod_confirmation.html', confirmation_code=confirmation_code)


# MongoDB Collections
users = mongo.db.users
products = mongo.db.products
orders = mongo.db.orders  # Make sure this line is present

@app.route('/verify_cod', methods=['POST'])
def verify_cod():
    entered_code = request.form['entered_code']
    confirmation_code = session.get('confirmation_code')

    if entered_code == confirmation_code:
        # If the entered code is correct, proceed to create the order
        shipping_details = session.get('shipping_details')

        if not shipping_details:
            return "Error: Shipping details not found. Please provide shipping information."

        # Use the phone number from the session
        phone = session.get('phone')  # Get the phone number from session (entered during login)

        if not phone:
            return "Error: Phone number not found. Please log in first."

        # Get the cart data using the phone number from login
        cart = get_cart_by_phone(phone)

        if not cart:
            return "Error: Cart is empty or not found for this phone number."

        # Log cart data to ensure correct values
        print(f"Order data cart: {cart}")

        # Construct order data
        order_data = {
            'phone': phone,

            'name': shipping_details['name'],
            'phno': shipping_details['phno'],
            'address': shipping_details['address'],
            'payment_method': shipping_details['payment_method'],
            'total_price': shipping_details['total_price'],
            'items': [
                {
                    'name': item['name'],
                    'item_id': item['productId'],  # Ensure correct field names
                    'price': item['price'],
                    'quantity': item['quantity']
                }
                for item in cart  # Ensure this loop is correctly mapping cart items
            ],
            'order_date': datetime.now(),
            'status': 'Pending'  # Set the order status to "Pending"
        }

        # Log the final order_data for debugging
        print(f"Final order data: {order_data}")

        # Insert the order into the MongoDB collection
        orders.insert_one(order_data)

        # ✅ Clear the user's cart after placing the order
        users.update_one({'phone': phone}, {'$set': {'cart': []}})


        # Clear the session after saving the order
        session.pop('shipping_details', None)
        session.pop('confirmation_code', None)

        return render_template('order_success.html', order_data=order_data)
    else:
        # If the code does not match, show an error message
        return render_template('cod_confirmation.html', error="The entered code is incorrect. Please try again.", confirmation_code=confirmation_code)












@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.run(debug=True)
