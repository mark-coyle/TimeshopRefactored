from flask import session, flash, redirect, url_for, render_template
from app.cart import bp
from app.helper import is_logged_in
from app import mysql
import time
import datetime


#Add to Cart
@bp.route('/cart/add/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def add(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("INSERT INTO `basket_items`(`basket_id` , `item_id`) VALUES(%s , %s)" , [users_basket , product_id])

    cur.execute("INSERT INTO `log`(`user_id` , `log_type` , `log_description` , `product_id`) VALUES(%s,%s,%s, %s)" , [user_id , "Stock" , "Product Added to Cart", product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('products.view' , id=  product_id))

#Remove From Cart
@bp.route('/cart/remove/<string:user_id>/<string:product_id>' , methods=['GET', 'POST' , 'DELETE'])
@is_logged_in
def remove(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'User ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("DELETE From `basket_items` where `basket_id` = %s AND  `item_id` = %s" , [users_basket , product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('products.view' , id=  product_id))

#Increase Quantity
@bp.route('/cart/increase_quantity/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def increase_quantity(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'User ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("UPDATE `basket_items` set `quantity` = `quantity` + 1 where `basket_id` = %s AND `item_id` = %s" , [users_basket , product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('account.index'))


#Remove From Cart
@bp.route('/cart/decrease_quantity/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def decrease_quantity(user_id , product_id):
    #Validate parameters
    if not (user_id is None):
        user_id = user_id
    else:
         error = 'User ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not (product_id is None):
        product_id = product_id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Insert Item into Basket_items
    cur = mysql.connection.cursor()

    #Get Users Basket ID
    basket_id =  session['basket_id']
    users_basket = basket_id['basket_id']

    cur.execute("UPDATE `basket_items` set `quantity` = `quantity` - 1 where `basket_id` = %s AND `item_id` = %s" , [users_basket , product_id])

    mysql.connection.commit()

    cur.close()


    return redirect(url_for('account.index'))



#Route For Showing Stock List
@bp.route('/checkout' , methods = ['GET' , 'POST'])
@is_logged_in
def checkout():
    #Get the Users Details
    user_id = session['user_id']
    user_basket = session['basket_id']

    basket_id = user_basket['basket_id']



    #Get Items in user basket
    cur = mysql.connection.cursor()
    item_count = cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s" , [basket_id])


    #If user has no items, redirect
    if item_count <= 0:
        flash("You Currently Have No Items to Checkout" , "danger")
        return redirect(url_for("account.index"))

    #Get Item Details
    if item_count > 0:
        basket_items = cur.fetchall()
        users_basket_items = []
    #Foreach Product, Retrieve the Product Details
    for product in basket_items:
        cur.execute("Select * from `products` where `product_id` = %s" , [product['item_id']])
        current_product = cur.fetchone()
        current_product['quantity'] = product['quantity']
        #Add Product to array
        users_basket_items.append(current_product)
    #Get Basket Total
    total = 0
    for item in users_basket_items:
         total += item['price'] * item['quantity']


    #Get Users Details
    cur.execute("SELECT * FROM `users` where `user_id` = %s" , [user_id])
    user = cur.fetchone()

    #get account details
    cur.execute("SELECT * FROM `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()


    mysql.connection.commit()
    cur.close()

    return render_template("views/account/checkout.html" , products = users_basket_items , total = total , user = user , account = account)


@bp.route('/confirmOrder' , methods = ['GET' , 'POST'])
@is_logged_in
def confirm_order():
    #Create Mysql cursor
    cur = mysql.connection.cursor()

    #Get Users Details:
    user_id = session['user_id']
    users_basket = session['basket_id']
    basket_id = users_basket['basket_id']

    cur.execute("SELECT * FROM `users` where `user_id` = %s" , [user_id])
    user = cur.fetchone()

    cur.execute("SELECT * FROM `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()


    #Set Order Date To Today
    created_at_time = time.time()
    order_date = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')

    #Get Basket Items
    cur = mysql.connection.cursor()
    item_count = cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s" , [basket_id])

    #If user has no items, redirect
    if item_count <= 0:
        flash("You Currently Have No Items to Checkout" , "danger")
        return redirect(url_for("account.index"))

    #Get Item Details
    if item_count > 0:
        basket_items = cur.fetchall()
        order_items = []

    #Foreach Product, Retrieve the Product Details
    for product in basket_items:
        cur.execute("Select * from `products` where `product_id` = %s" , [product['item_id']])
        current_product = cur.fetchone()
        current_product['quantity'] = product['quantity']
        #Add Product to array
        order_items.append(current_product)


    #Calculate Order Total
    order_total = 0
    for item in order_items:
        order_total += item['price'] * item['quantity']
        #Update Stock Levels
        cur.execute("UPDATE `order_stock_levels` set `amount` = `amount` - %s where `item_id` = %s " , [item['quantity'] , item['product_id']])



    #Update Order Table
    cur.execute("INSERT INTO `orders`(`order_total` , `order_date` , `shipping_address` , `user_id`) VALUES(%s, %s, %s ,%s)" , [order_total,order_date,account['shipping_address'],user_id])

    #Get Order ID
    cur.execute("SELECT * from `orders` where  `user_id` = %s AND `order_date` = %s" , [user_id, order_date])
    order_id = cur.fetchone()

    for item in order_items:
        #Update Order Items
        cur.execute("INSERT INTO `order_items`(`item_id`,`order_id`) VALUES(%s, %s)" , [item['product_id'] , order_id['order_id']])

    #Reset Users Basket
    cur.execute("DELETE FROM `basket_items` where `basket_id` = %s" , [basket_id])

    #update log table

    cur.execute("INSERT INTO `log`(`user_id` , `order_id`,`log_type` , `log_description` ) VALUES(%s,%s,%s,%s)" , [user_id , order_id['order_id'] ,"Order" , "Order Completed"])


    mysql.connection.commit()
    cur.close()

    return redirect(url_for('account.index'))
