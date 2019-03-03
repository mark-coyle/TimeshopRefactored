from flask import redirect, url_for, session, flash, request, render_template
from app.account import bp
from app.account.forms import EditAccountForm, PasswordChangeForm
from app.helper import is_logged_in
from app import mysql

@bp.route('/account')
@is_logged_in
def index():
    form = PasswordChangeForm(request.form)
    user_id = session['user_id']

    #Get user details
    #Create cursor
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM users WHERE user_id = %s", [user_id])
    user = cur.fetchone()

    #Get users account details
    cur.execute("SELECT * FROM `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()

    #Get Users Orders
    order_count =  cur.callproc('getOrdersByUser' , [user_id])

    if order_count:
        orders = cur.fetchall()
        order_total = 0
        for order in orders:
            order_total += order['order_total']
    else:
        orders = 0
        order_total = 0


    #get users liked products
    liked_count = cur.execute("Select * from `product_likes` where `user_id` = %s" , [user_id])


    if liked_count > 0:
        liked_products = cur.fetchall()
        users_liked_products = []
        #Foreach Liked Product, Retrieve the Product Details
        for product in liked_products:
            cur.execute("Select * from `products` where `product_id` = %s" , [product['product_id']])
            current_product = cur.fetchone()

            #Add Product to array
            users_liked_products.append(current_product)

    else:
        users_liked_products = 0

    #Get Products in Basket
    basket_id = session['basket_id']

    #Check for basket_id , Admins wont have one
    if basket_id:
        users_basket = basket_id['basket_id']
    else:
        users_basket = False

    #If no basket
    if users_basket:
        basket_count = cur.execute("SELECT * FROM `basket_items` where `basket_id` = %s" , [users_basket])
    else:
        basket_count = 0



    if basket_count > 0:
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

    else:
        users_basket_items = 0
        total = 0



    #close connection
    cur.close()

    return render_template('views/account.html' , user = user, account = account, orders = orders , liked_products = users_liked_products  , basket = users_basket_items, form = form , order_total = order_total,total = total )


@bp.route('/account/edit/<string:id>' , methods=['GET' , 'POST'])
@is_logged_in
def edit(id):
    form = EditAccountForm(request.form)

    #Validate ID
    if not (id is None):
        user_id = id
    else:
         error = 'Product ID is invalid'
         return render_template('views/product/list.html', error=error)

    #Pre Populate Form
    cur = mysql.connection.cursor()

    #Get users details
    cur.execute("Select * from `users` where user_id = %s", [user_id])
    user = cur.fetchone()

    #Get account details
    cur.execute("SELECT * from `accounts` where `user_id` = %s" , [user_id])
    account = cur.fetchone()

    #commit to db
    mysql.connection.commit()


    #Pre populate the form
    form.first_name.data = user['first_name']
    form.last_name.data = user['last_name']
    form.username.data = user['username']
    form.email.data = user['email']
    form.shipping_address.data = account['shipping_address']

    if request.method == "POST" and form.validate():
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        shipping_address = request.form['shipping_address']

        #Further Check for username, to ensure there is no other username the same

        if username != form.username.data:
            cur.execute("SELECT * FROM `users` where `username` = %s" , [username])
            result = cur.fetchone()

            if result:
                flash("That username is already taken" , 'danger')
                return redirect(url_for('account.edit'))


        cur.execute("UPDATE `users` set `first_name` = %s , `last_name` = %s ,`username` = %s ,`email` = %s  where `user_id` = %s" , [first_name , last_name , username , email , user_id])
        #commit to db
        mysql.connection.commit()

        cur.execute("UPDATE `accounts` set `shipping_address` = %s where `user_id` = %s" , [shipping_address , user_id] )
        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        #success message
        flash('Your Account Has been Updated', 'success')

        return redirect(url_for('account.index'))

    return render_template('views/account/edit.html', form = form)

@bp.route('/account/delete/<int:id>' , methods=['GET' , 'POST'])
@is_logged_in
def delete(id):
    #ensure logged in user is deleting their own account
    user_id = session['user_id']
    basket = session['basket_id']
    basket_id = basket['basket_id']

    print(id)
    print(user_id)

    if(id != user_id):
        flash('You cant access this function currently. ' , 'danger')
        return redirect(url_for('account.index'))
    else:
        #User deleting their own account

        #setup mysql
        cur = mysql.connection.cursor()

        #Remove users account
        cur.execute('DELETE FROM `accounts` where `user_id` = %s' , [user_id])

        #Remove users basket items
        cur.execute('DELETE FROM `basket_items` where `basket_id` = %s' , [basket_id])

        #Remove users basket
        cur.execute('DELETE FROM `user_basket` where `user_id` = %s' , [user_id])

        #Remove user from users table
        cur.execute('DELETE FROM `users` where `user_id` = %s' , [user_id])

        #Commit
        mysql.connection.commit()

        #Close mysql
        cur.close()
        session.clear()

        return redirect(url_for('auth.login'))
