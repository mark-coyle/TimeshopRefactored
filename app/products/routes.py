from flask import render_template, session, url_for, redirect, flash, request
from app.products import bp
from app.products.forms import AddProductForm, EditProductForm, ReviewForm
from app.helper import is_admin, is_logged_in
from app import mysql
import time
import datetime
import json

@bp.route('/Product/add',methods=['GET' , 'POST'])
@is_admin
def add():
    form = AddProductForm(request.form)

    # #Get Enum Select Values
    # #Create cursor
    # cur = mysql.connection.cursor()

    # cur.execute("SHOW COLUMNS FROM products LIKE 'type'")
    # values = cur.fetchone()
    # types = values['Type']



    # print("values" ,types)
    # #commit to db
    # mysql.connection.commit()

    # #close connection
    # cur.close()

    # Check if get or post
    if request.method == "POST" and form.validate():
        name = form.name.data
        product_type = form.product_type.data
        product_description = form.description.data
        product_price = form.price.data
        product_image = request.files[form.image.name]
        created_at_time = time.time()
        date_added = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')

        #Get quantity
        quantity = form.quantity.data

        if product_image and allowed_file(product_image.filename):
            filename = secure_filename(product_image.filename)
            product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #Create cursor
        cur = mysql.connection.cursor()

        #Validate this product doesn't exist
        cur.execute("SELECT * FROM `products` where name = %s" , [name])
        product_test = cur.fetchone()

        if product_test:
            flash('This product already exists' , 'warning')
            return redirect(url_for('products.view' , id = product_test['product_id']))

        #create product
        cur.execute("INSERT INTO products(`name`,`type`,`description` , `price`, `image`, `date_added`) VALUES(%s, %s, %s, %s , %s, %s)", (name,product_type,product_description,product_price, filename,date_added))

        #get product id
        cur.execute("SELECT * FROM `products` where name = %s" , [name])
        product = cur.fetchone()

        #update quantity
        cur.execute("INSERT INTO `order_stock_levels`(`item_id` , `amount` , `stock_tolerance`) VALUES(%s , %s , %s) " , [product['product_id'] , quantity , 2])

        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #success message
        flash('This Product has been added successfully', 'success')

        return redirect(url_for('admin.stocklist'))


    return render_template('views/product/add.html' , form = form )

@bp.route('/Product/edit/<string:id>' , methods=['GET', 'POST'])
@is_admin
def edit(id):
    form = EditProductForm(request.form)
    #Validate ID
    if not (id is None):
        product_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Get Product Details
    cur = mysql.connection.cursor()

    cur.execute("Select * from products where product_id = %s", [product_id])
    product = cur.fetchone()

    #get quantity details
    cur.execute("Select * from order_stock_levels where item_id = %s" , [product['product_id']])
    quantity = cur.fetchone()

    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    #Pre populate the form
    form.name.data = product['name']
    form.description.data = product['description']
    form.price.data = product['price']
    form.quantity.data = quantity['amount']




    #Handle Product Update
    # Check if get or post
    if request.method == "POST" and form.validate():
        name = request.form['name']
        product_type = request.form['product_type']
        product_description = request.form['description']
        product_price = request.form['price']
        product_quantity = request.form['quantity']
        product_image = request.files[form.image.name]

        #parse file

        if product_image and allowed_file(product_image.filename):
            filename = secure_filename(product_image.filename)
            product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            #no image supplied re input file value
            filename = product['image']


        #Create cursor
        cur = mysql.connection.cursor()

        cur.execute("UPDATE `products` set `name` = %s , `type` = %s , `description`= %s , `price` = %s , `image` = %s WHERE `product_id` = %s" , [name , product_type , product_description , product_price , filename , product_id])

        #update stock quantity record
        cur.execute("UPDATE `order_stock_levels` set `amount` = %s where `item_id` = %s" , [product_quantity , product_id])
        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #success message
        flash('This Product has been updated successfully', 'success')

        return redirect(url_for('admin.stocklist'))
    return render_template('views/product/edit.html' , product = product , form = form)

@bp.route('/delete_product/<string:id>' , methods=['GET', 'POST'])
@is_admin
def delete(id):
    #Validate ID
    if not (id is None):
        product_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

     #Create cursor
    cur = mysql.connection.cursor()

    cur.execute("DELETE from `products` where product_id = %s", [product_id])
    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    flash("This Product has been Deleted" , "success")
    return redirect(url_for('admin.stocklist'))


@bp.route('/Product/view/<string:id>' , methods =['GET' , 'POST'])
def view(id):
    #Validate ID
    if not (id is None):
        product_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    if not id.isnumeric():
        abort(404)
     #Get Product Details
    cur = mysql.connection.cursor()

    cur.execute("Select * from products where product_id = %s", [product_id])
    product = cur.fetchone()

    #Pass user details
    user_id = session['user_id']
    cur.execute("Select * from `users` where `user_id` = %s" , [user_id])
    user = cur.fetchone()

    #Get Basket ID from Session
    basket_id = session['basket_id']

    if basket_id:
        users_basket = basket_id['basket_id']
    else:
        users_basket = False

    #Check if Item is in Cart
    cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s AND `item_id` = %s" , [users_basket , product_id])
    basket_items = cur.fetchone()

    if basket_items:
        #Currently in Cart
        item_in_cart = True
    else:
        #not in cart
        item_in_cart = False


    #Check if user has liked this product
    cur.execute("SELECT * FROM `product_likes` WHERE `user_id` = %s AND `product_id` = %s" , [user_id , product_id])
    res = cur.fetchone()

    if res:
        #User has liked this product
        user_liked = True
    else:
        user_liked = False

    #Get Count of Product Likes
    cur.execute("SELECT COUNT(`product_id`) as `product_like_count` from `product_likes` where `product_id` = %s" , [product_id])
    like_count = cur.fetchone()

    #Check how many times product has been ordered
    cur.execute("SELECT COUNT(`item_id`) as `order_count` from `order_items` where `item_id` = %s" , [product_id])
    order_count = cur.fetchone()

    #Get Similar Products
    cur.execute("SELECT * from `products` where `type` = %s and `product_id` != %s LIMIT 3" , [product['type'] , product_id])
    similar_list = cur.fetchall()

    #Get Review Information
    cur.execute("SELECT * from `reviews` where `product_id` = %s ORDER BY `datetime` DESC LIMIT 5" , [product_id])
    reviews_list = cur.fetchall()

    #Validate
    if reviews_list:
        reviews = reviews_list
        for review in reviews:
            cur.execute("SELECT * FROM `users` where `user_id` = %s" , [review['user_id']])
            current_user = cur.fetchone()
            review['username'] = current_user['username']
    else:
        reviews = False

    #Check product quantity
    cur.execute("SELECT * FROM `order_stock_levels` where `item_id` = %s" , [product_id])
    stock = cur.fetchone()



    #commit to db
    mysql.connection.commit()

    #close connection
    cur.close()

    return render_template('views/product/view.html', product = product ,reviews = reviews, stock = stock,user = user , user_liked = user_liked ,like_count = like_count, order_count = order_count,item_in_cart = item_in_cart , similar_products = similar_list)


#Route For Liking Product
@bp.route('/LikeProduct/<string:user_id>/<string:product_id>' , methods=['GET', 'POST'])
@is_logged_in
def like(user_id , product_id):
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

    #Validate ID's Preform Like Request
    cur = mysql.connection.cursor()
    created_at_time = time.time()
    liked_at = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')
    #Get Todays date


    cur.execute("INSERT INTO  `product_likes` (`product_id` , `user_id` , `date_liked`) VALUES(%s , %s , %s)" , [product_id , user_id, liked_at])
    # cur.execute("INSERT INTO `log`(`user_id` , `log_type` , `log_description` , `product_id`) VALUES(%s,%s,%s, %s)" , [user_id , "Stock" , "Product Liked", product_id])

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('products.view' , id = product_id))

#Route For Unliking Product
@bp.route('/UnlikeProduct/<string:user_id>/<string:product_id>' , methods=['GET', 'POST' , 'DELETE'])
@is_logged_in
def unlike(user_id , product_id):
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

    #Validate ID's Preform Like Request
    cur = mysql.connection.cursor()
    created_at_time = time.time()
    liked_at = datetime.datetime.fromtimestamp(created_at_time).strftime('%Y-%m-%d %H:%M:%S')
    #Get Todays date


    cur.execute("DELETE from `product_likes` WHERE `user_id` = %s AND `product_id` = %s" , [user_id , product_id])

    mysql.connection.commit()

    cur.close()

    return redirect(url_for('products.view' , id=  product_id))

#Product Review:
@bp.route("/Product/review/<string:product_id>/<string:user_id>" , methods = ['GET' , 'POST'])
@is_logged_in
def review(product_id , user_id):
    #Validate Inputs
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

    #Check if user has already submitted a Review
    #preprare mysql
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM `reviews` where user_id = %s AND product_id = %s" , [user_id , product_id])
    reviewed = cur.fetchone()


    if reviewed:
        #Already Reviewed , redirect
        flash('You have already reviewed this product' , 'warning')
        return redirect(url_for('products.view' , id=  product_id))

    #Get Review Form
    form = ReviewForm(request.form)

    #Handle Submission
    if request.method == "POST" and form.validate():
        title = form.title.data
        description = form.description.data
        reviewed_time = time.time()
        review_date = datetime.datetime.fromtimestamp(reviewed_time).strftime('%Y-%m-%d %H:%M:%S')

        cur.execute("INSERT INTO `reviews`(`title` , `description` , `datetime` , `user_id` , `product_id`) VALUES(%s,%s,%s,%s,%s)" , [title , description , review_date , user_id , product_id])

        #commit query
        mysql.connection.commit()

        #close db connection
        cur.close()

        #redirect
        return redirect(url_for('products.view' , id=  product_id))



    return render_template('views/product/review.html' , form = form )

@bp.route('/GetProductLikes' , methods=['GET'])
@is_admin
def get_likes():
    #get the like data return as json.

    #mysql
    cur = mysql.connection.cursor()
    cur.execute("SELECT `product_id`, COUNT(`product_id`) as likes FROM `product_likes` Group BY `product_id` ")
    like_list = cur.fetchall()

    #get product names and types
    #empty like list
    likes = []
    for product in like_list:
        cur.execute("Select `name` , `type` from `products` where `product_id` = %s", [product['product_id']])
        current_product = cur.fetchone()
        current_product['amount'] = product['likes']
        #add to new list
        likes.append(current_product)

    #Return Data in Correct Format
    likes = json.dumps(likes)
    cur.close()

    return likes
