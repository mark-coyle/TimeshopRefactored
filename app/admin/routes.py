from flask import redirect, url_for, session, flash, render_template
from app.admin import bp
from app.admin.forms import PasswordResetAdminForm
from app.helper import is_admin
from app import mysql


@bp.route('/stocklist')
@is_admin
def stocklist():
    # Get Product List
    cur = mysql.connection.cursor()

    product_count = cur.execute("Select * from products")

    # Get Quantitys For products
    if product_count > 0:
        products = cur.fetchall()
        stock_items = []
    # Foreach Product, Retrieve the Product Details
    for product in products:
        cur.execute(
            "Select * from `order_stock_levels` where `item_id` = %s", [product['product_id']])
        current_product = cur.fetchone()
        product['quantity'] = current_product['amount']
        product['tolerance'] = current_product['stock_tolerance']
        if product['quantity'] < product['tolerance']:
            product['stock_status'] = 'Under Tolerance'

        else:
            product['stock_status'] = 'Above Tolerance'
        # Add Product to array
        stock_items.append(product)

    # Logic for Stock Issues

    # commit to db
    mysql.connection.commit()

    # close connection
    cur.close()

    return render_template('views/product/list.html', product_list=stock_items)


@bp.route('/users/manage', methods=['GET', 'POST'])
@is_admin
def user_manager():
    # Get All Users
    cur = mysql.connection.cursor()
    account_list = cur.execute(
        "SELECT * FROM `accounts` WHERE `account_type` = %s", ["User"])
    accounts = cur.fetchall()

    # Get Users
    user_list = []
    for i in accounts:
        cur.execute("SELECT * FROM `users` where `user_id` = %s",
                    [i['user_id']])
        user = cur.fetchone()
        i['username'] = user['username']
        user_list.append(i)

    cur.close()

    return render_template('views/admin/usermanager.html', users=user_list)


@bp.route('/users/block/<string:id>', methods=['GET', 'POST'])
@is_admin
def block_account(id):
     # Validate ID
    if not (id is None):
        user_id = id
    else:
        error = 'User ID is invalid'
        return render_template('views/admin/usermanager.html', error=error)

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE `accounts` set `account_status` = 1 where user_id = %s", [user_id])

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('admin.user_manager'))


@bp.route('/users/unblock/<string:id>', methods=['GET', 'POST'])
@is_admin
def unblock_account(id):
     # Validate ID
    if not (id is None):
        user_id = id
    else:
        error = 'User ID is invalid'
        return render_template('views/admin/usermanager.html', error=error)

    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE `accounts` set `account_status` = 0 where user_id = %s", [user_id])

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('admin.user_manager'))


@bp.route('/resetpassword/<string:id>', methods=['GET', 'POST'])
@is_admin
def password_reset(id):
    form = PasswordResetAdminForm(request.form)
    # Validate ID
    if not (id is None):
        user_id = id
    else:
        error = 'User ID is invalid'
        return render_template('views/admin/usermanager.html', error=error)

    cur = mysql.connection.cursor()
    # pass user details to view
    cur.execute("SELECT * FROM `users` where `user_id` = %s", [user_id])
    user = cur.fetchone()

    # Check if it matches current password
    current_password = user['password']
    password_reset = sha256_crypt.encrypt(str(form.password.data))

    if sha256_crypt.verify(current_password, password_reset):
        error = 'Passwords cannot remain the same'
        return render_template('views/admin/usermanager.html', error=error)

    cur.execute("UPDATE `users` set `password` = %s where user_id = %s", [
                password_reset, user_id])

    mysql.connection.commit()
    cur.close()

    return render_template('views/admin/passwordreset.html', form=form, user=user)
