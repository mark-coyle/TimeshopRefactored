from flask import redirect, session, flash, url_for, render_template, request
from app.orders import bp
from app.helper import is_admin
import json
import time
import datetime


@bp.route('/getOrderData', methods=['GET'])
@is_admin
def get_order_data():
    # mysql
    cur = mysql.connection.cursor()

    cur.execute("SELECT `order_total` , `order_date` from `orders` ")
    data = cur.fetchall()

    # Group Orders By Months
    cur.execute("SELECT month(`order_date`) as `month` , SUM(`order_total`) as `month_total` from `orders` GROUP BY month(`order_date`)")
    totals = cur.fetchall()

    # add month_orders to totals
    total_test = []
    for key in totals:
        # Create Nested Orders Array
        key['orders'] = []
        cur.execute("SELECT `order_total` , `order_date` from `orders` where month(`order_date`) = %s", [
                    key['month']])
        # Get Month Name From number
        key['month'] = datetime.date(1900, key['month'], 1).strftime('%B')
        orders = cur.fetchall()
        for order in orders:
            order['order_date'] = datetime.datetime.date(
                order['order_date']).isoformat()
            key['orders'].append(order)

        total_test.append(key)

    # Format Data
    for d in data:
        d['order_date'] = datetime.datetime.date(d['order_date']).isoformat()

    cur.close()

    data = json.dumps(total_test)
    return data


@bp.route('/orderReport', methods=['GET', 'POST'])
@is_admin
def order_report():
    order_data = []
    # Get All Months That have Orders
    # Create Sql
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT month(`order_date`) as months from `orders` group by months")
    data = cur.fetchall()

    # convert to month name
    for i in data:
        # Get Month Name From number
        i['month_value'] = i['months']
        i['months'] = datetime.date(1900, i['months'], 1).strftime('%B')

    cur.close()

    if request.method == "POST":
        # Handle User Input
        month_chosen = request.form.get('month')

        # Create Sql
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * from `orders` WHERE month(`order_date`) =%s", [month_chosen])
        orders = cur.fetchall()

        # get user data & order item data
        order_data = []
        for i in orders:
            cur.execute(
                "SELECT * FROM `users` where `user_id` = %s", [i['user_id']])
            current_user = cur.fetchone()

            cur.execute(
                "SELECT * FROM `accounts` where `user_id` = %s", [i['user_id']])
            current_account = cur.fetchone()
            # cur.execute("SELECT * from `order_items` where `order_id` = %s" ,[i['order_id']] )
            # current_item = cur.fetchone()

            # Get item details
            # cur.execute("SELECT * from `products` where `product_id` = %s" , [current_item['item_id']])
            # item_info = cur.fetchone()

            i['fname'] = current_user['first_name']
            i['lname'] = current_user['last_name']
            i['shipped_to'] = current_account['shipping_address']
            # i['item_name'] = item_info['name']
            # i['item_description'] = item_info['description']
            order_data.append(i)

        cur.close()

    return render_template('views/admin/report.html', data=data, orders=order_data)
