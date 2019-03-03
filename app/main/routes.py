from flask import session, redirect, url_for, session, flash, render_template, abort
from app.main import bp
from app.helper import is_admin, is_logged_in
from app import mysql
import time
import datetime


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/control')
@is_admin
def Control():
    # get view data
    # Create cursor
    cur = mysql.connection.cursor()

    cur.execute("Select Count(*) as count from products")
    count = cur.fetchone()

    # Get total orders
    cur.callproc('getOrderTotal')
    order_total = cur.fetchone()

    # Get total users
    cur.execute(
        "SELECT COUNT(*) as count from `accounts` where  `account_type` = %s", ["User"])
    total_users = cur.fetchone()

    # Get Currently Logged In Users
    cur.execute(
        "SELECT COUNT(*) as user_count from `accounts` where `logged_in` = %s", [1])
    current_users = cur.fetchone()

    # Get Todays Orders
    todays_time = time.time()
    todays_timestamp = datetime.datetime.fromtimestamp(
        todays_time).strftime('%Y-%m-%d %H:%M:%S')

    cur.execute("SELECT COUNT(`order_id`) as orders from `log` where `log_time` = %s", [
                todays_timestamp])
    todays_orders = cur.fetchone()

    # Get Average Users {Check Log Table For Logins With Timestamp And Divide}

    # Get Average Orders {Check Log Table For Orders With Timestamp And Divide}

    # commit to db
    mysql.connection.commit()

    # close connection
    cur.close()

    return render_template('views/control.html', count=count, current_users=current_users, todays_orders=todays_orders, order_total=order_total, total_users=total_users)


# Product Category Views
@bp.route('/<string:name>', methods=['GET', 'POST'])
@is_logged_in
def Category(name):
    # Validate name
    if name == '':
        flash('The Product Type Is incorrect', 'warning')
        return redirect(url_for('main.home'))

    acceptable_urls = ['ClassicWatches',
                       'ModernWatches', 'SmartWatches', 'PocketWatches']
    if name not in acceptable_urls:
        flash('The Product Type Is incorrect', 'warning')
        abort(404)

    # Add space to category type
    name = name.replace("Watches", " Watch")

    # Setup Cursor
    cur = mysql.connection.cursor()
    cur.callproc('getProductsByType', [name])
    results = cur.fetchall()

    return render_template('views/product/category.html', watches=results)


@bp.route('/home')
@is_logged_in
def home():
    # Get data for home dashboard
    cur = mysql.connection.cursor()
   # Check if product data is cached:
    # if(newAdditions_collection.count() > 0 ):
    #     #Use Data from here
    #     res = newAdditions_collection.find({})
    #     new_additions = []

    #     for doc in res:
    #         product={}
    #         product['product_id'] = doc['product_id']
    #         product['name'] = doc['name']
    #         product['description'] = doc['description']
    #         product['price'] = doc['price']
    #         product['type'] = doc['type']
    #         product['image'] = doc['image']
    #         product['date_added'] = doc['date_added']
    #         new_additions.append(product)

    # elif(newAdditions_collection.count() <= 0):
    # Cache doesn't exist

    # return user if username exists
    res = cur.execute(
        "SELECT * FROM `products` ORDER BY `date_added` DESC LIMIT 5")
    new_additions = cur.fetchall()

    # push products to mongo
    # for p in new_additions:
    #     p['date_added'] = datetime.datetime.date(p['date_added']).isoformat()
    #     #product = json.dumps(p)
    #     doc = {
    #         "product_id": p['product_id'],
    #         "name":p['name'],
    #         "description":p['description'],
    #         "type":p['type'],
    #         "price":p['price'],
    #         "image":p['image'],
    #         "date_added":p['date_added'],
    #         "date":utc_time
    #     }
    #     newAdditions_collection.insert_one(doc)

    # Check MongoDB Cache
    # if(most_popular_collection.count() > 0):
    #     #Cache Exists
    #     product_count = most_popular_collection.count()
    #     res = most_popular_collection.find({})
    #     product_info = []

    #     for doc in res:
    #         product={}
    #         product['product_id'] = doc['product_id']
    #         product['name'] = doc['name']
    #         product['description'] = doc['description']
    #         product['like_count'] = doc['product_like_count']
    #         product_info.append(product)

    # elif(most_popular_collection.count() <= 0):
    # Cache doesn't exist

    # Return Most popular Products
    product_count = cur.execute(
        "SELECT `product_id` , COUNT(`product_id`) as `product_like_count` from `product_likes` GROUP BY `product_id` ORDER BY `product_like_count` DESC LIMIT 5")
    product_like_info = cur.fetchall()
    # If theres likes, get product info
    if product_count <= 0:
        products = 0

    # Get Product Details
    if product_count > 0:
        product_info = []
        # Foreach Product, Retrieve the Product Details
        # push products to mongo
        for p in product_like_info:
            cur.execute(
                "Select * from `products` where `product_id` = %s", [p['product_id']])
            current_product = cur.fetchone()
            current_product['like_count'] = p['product_like_count']
            doc = {
                "product_id": current_product['product_id'],
                "name": current_product['name'],
                "description": current_product['description'],
                "product_like_count": current_product['like_count'],
                # "date":utc_time

            }
            # most_popular_collection.insert_one(doc)
            # Add Product to array
            product_info.append(current_product)

    return render_template('home.html', new_additions=new_additions, products=product_info)
