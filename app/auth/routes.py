from flask import redirect, request, url_for, render_template, session, flash
from passlib.hash import sha256_crypt
from app.auth.forms import PasswordChangeForm, LoginForm, RegisterForm
from app.auth import bp
from app.helper import is_admin, is_logged_in
from app import mysql


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Load in form
    form = LoginForm(request.form)
    # Check if get or post
    if request.method == "POST" and form.validate():
        # get username and password
        username = request.form['username']
        password = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # return user if username exists
        cur.callproc('getUserByUsername', [username])
        res = cur.fetchone()
        #res = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if res:
            # user exists , get password
            password_hashed = res['password']

            # Get users account details
            cur.execute(
                "SELECT * FROM `accounts` where `user_id` = %s", [res['user_id']])
            account = cur.fetchone()

            # Check if account is blocked
            if account['account_status'] != 0:
                error = 'This Account is currently Blocked'
                return render_template('login.html', error=error)

            # Check passwords match
            if sha256_crypt.verify(password, password_hashed):
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = res['user_id']
                session['user_type'] = account['account_type']
                session['account_id'] = account['account_id']

                # Get users Basket
                cur.execute("SELECT `basket_id` from `user_basket` where `user_id` = %s", [
                            res['user_id']])
                session['basket_id'] = cur.fetchone()

                # Update Logged In Status
                cur.execute("Update `accounts` set `logged_in` = %s where `account_id` = %s", [
                            1, session['account_id']])

                # check User is admin
                if session['user_type'] == "Admin":
                    flash('You have successfully logged in', 'success')
                    return redirect(url_for('main.Control'))

                # update Log table
                user_id = res['user_id']
                # log = cur.execute("INSERT INTO `log`(`user_id` , `log_type` , `log_description`) VALUES(%s,%s,%s)" , [user_id , "Account" , username + " has logged in"])

                mysql.connection.commit()

                flash('You have successfully logged in', 'success')
                return redirect(url_for('main.home'))

            else:
                # passwords dont match
                error = 'Passwords do not match'
                return render_template('login.html', error=error)

            # close connection
            cur.close()

        else:
            # No username found
            error = 'That Username is currently not registered'
            return render_template('login.html', error=error)

    return render_template('login.html')


@bp.route('/logout')
@is_logged_in
def logout():

        # Create cursor
    cur = mysql.connection.cursor()
    # Update Logged In Status

    cur.execute("UPDATE `accounts` set `logged_in` = %s where account_id = %s", [
                0, session['account_id']])

    # commit to db
    mysql.connection.commit()

    # close connection
    cur.close()

    # clear session
    session.clear()

    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/signup', methods=['GET', 'POST'])
def sign_up():
    # Load in form
    form = RegisterForm(request.form)

    # Check if get or post
    if request.method == "POST" and form.validate():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        created_at_time = time.time()
        created_at = datetime.datetime.fromtimestamp(
            created_at_time).strftime('%Y-%m-%d %H:%M:%S')
        user_type = "User"

        # Create cursor
        cur = mysql.connection.cursor()

        # Preform Validation Checks
        cur.execute("SELECT * FROM `users` WHERE `username` = %s", [username])
        username_check = cur.fetchone()

        if username_check:
            # Username already in use
            flash("This username is already in use, pick another", 'warning')
            return redirect(url_for("auth.sign_up"))

        # Preform Validation Checks
        cur.execute("SELECT * FROM `users` WHERE `email` = %s", [email])
        email_check = cur.fetchone()

        if email_check:
            # Email already in use
            flash("This email is already in use, pick another", 'warning')
            return redirect(url_for("auth.sign_up"))

        # Validated Data , Continue

        # Create User
        res = cur.execute("INSERT INTO users(`first_name`,`last_name` , `username`,`email`, `password`) VALUES(%s, %s, %s,%s, %s )",
                          (first_name, last_name, username, email, password))
        user = cur.lastrowid

        # Create User account
        res = cur.execute(
            "INSERT INTO accounts(`user_id`,`created_at`,`account_type`) VALUES(%s, %s, %s)", (user, created_at, user_type))

        # get users ID
        if res:
            cur.execute(
                "SELECT * FROM `users` where `username` = %s", [username])
            user = cur.fetchone()

        # commit to db
        mysql.connection.commit()

        # close connection
        cur.close()

        # success message
        flash('Your Account Has been created', 'success')

        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)


@bp.route('/login/<string:guest>', methods=['GET', 'POST'])
def guest(guest):
    if(guest != "guest"):
        return redirect(url_for('auth.login'))
    else:
        session['logged_in'] = True
        session['user_type'] = 'Guest'
        session['user_id'] = 0
        session['basket_id'] = 0
        return redirect(url_for('main.home'))


@bp.route('/password_change/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def change_password(id):
    form = PasswordChangeForm(request.form)
    # Validate ID
    if not (id is None):
        user_id = id
    else:
        error = 'Product ID is invalid'
        return render_template('views/product/list.html', error=error)

    if request.method == "POST" and form.validate():
        current_password = form.current_password.data
        new_password = form.new_password.data

        # Check current password matches the one in database
        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE user_id = %s", [user_id])
        user = cur.fetchone()
        password_hashed = user['password']

        if sha256_crypt.verify(current_password, password_hashed):
            # passwords match
            password = sha256_crypt.encrypt(str(form.new_password.data))

            cur.execute('UPDATE `users` set `password` = %s WHERE `user_id` = %s', [
                        password, user_id])

            # commit to db
            mysql.connection.commit()

            # close connection
            cur.close()

            # success message
            flash('Your Password Has been updated', 'success')
            return redirect(url_for('auth.logout'))

        else:
            # passwords dont match
            flash('Password Incorrect', 'danger')
            return redirect(url_for('account.index'))

    else:
        flash(
            'Please Ensure All Fields Are Filled, and That your passwords match', 'danger')
        return redirect(url_for('account.index'))
