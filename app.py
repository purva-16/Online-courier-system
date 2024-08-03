from msilib import add_data
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pyodbc
from operator import itemgetter

  
app = Flask(__name__,static_folder='static', static_url_path='/static')
app.secret_key = 'xyzsdfg'

conn = pyodbc.connect('DRIVER={SQL Server};SERVER=DESKTOP-IIROG91;DATABASE=backup for dbms;')


@app.route('/')
def home():
    return render_template('home.html')
    
    
@app.route('/alogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute(f"SELECT [a_id] FROM [backup for dbms].[dbo].[adlogin] WHERE [email] = ? AND [password] = ?", (email, password))
        admin_id = cursor.fetchone()

        if admin_id:
            session['admin_id'] = admin_id[0]
            return redirect(url_for('adashboard'))  # Corrected here
  # Corrected here
        else:
            return render_template('ad_login.html', error='Invalid email or password')

    return render_template('ad_login.html') 



@app.route('/ulogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT [u_id] FROM [backup for dbms].[dbo].[userlogin] WHERE [email] = ? AND [password] = ?", (email, password))
        user_id = cursor.fetchone()

        if user_id:
            session['user_id'] = user_id[0]
            return redirect(url_for('user_dashboard'))
    else:
        # If request method is GET, render the login page
        return render_template('user_login.html')


@app.route('/adashboard')
def admin_dashboard():
    cursor = conn.cursor()

    # Fetch data from the 'merged_table'
    cursor.execute("SELECT TOP (1000) [cid], [BILLNO], [u_id], [a_id], [city], [state], [country], [REMAIL], [RPHONE], [RADDRESS], [SNAME], [SEMAIL], [SPHONE], [SADDRESS] FROM [backup for dbms].[dbo].[merged_table]")
    merged_data = cursor.fetchall()

    # Fetch data from the 'user' table
    cursor.execute("SELECT TOP (1000) [u_id], [name], [email], [phone], [a_id], [city], [state], [country] FROM [backup for dbms].[dbo].[user]")
    user_data = cursor.fetchall()

    # Fetch data from the 'Transactions' table
    cursor.execute("SELECT TOP (1000) [BILLNO], [DATE], [RNAME], [U_ID], [A_ID] FROM [backup for dbms].[dbo].[Transactions]")
    transactions_data = cursor.fetchall()

    # Fetch data from the 'UserRating' table
    cursor.execute("SELECT TOP (1000) [u_id], [comment_id], [rating], [email] FROM [backup for dbms].[dbo].[UserRating]")
    user_rating_data = cursor.fetchall()

    # Fetch data from the 'comment' table
    cursor.execute("SELECT TOP (1000) [email], [title], [comment], [u_id], [date], [rating], [ratings] FROM [backup for dbms].[dbo].[comment]")
    comment_data = cursor.fetchall()

    cursor.close()

    return render_template('admin_dashboard.html', merged_data=merged_data, user_data=user_data, transactions_data=transactions_data, user_rating_data=user_rating_data, comment_data=comment_data)

@app.route('/courier')
def courier_page():
    # Fetch courier information
    cursor = conn.cursor()
    cursor.execute("SELECT [cid], [BILLNO], [u_id], [a_id] FROM [backup for dbms].[dbo].[courier]")
    couriers = cursor.fetchall()

    # Fetch sender information
    cursor.execute("SELECT [BILLNO], [SNAME], [SEMAIL], [SPHONE], [SADDRESS] FROM [backup for dbms].[dbo].[Senders]")
    senders = cursor.fetchall()

    # Fetch receiver information
    cursor.execute("SELECT [BILLNO], [REMAIL], [RPHONE], [RADDRESS] FROM [backup for dbms].[dbo].[Receivers]")
    receivers = cursor.fetchall()

    return render_template('courier.html', couriers=couriers, senders=senders, receivers=receivers)


@app.route('/transactions')
def transactions_page():
    # Fetch transaction information
    cursor = conn.cursor()
    cursor.execute("SELECT [BILLNO], [DATE], [RNAME], [U_ID], [A_ID] FROM [backup for dbms].[dbo].[Transactions]")
    transactions = cursor.fetchall()

    return render_template('transactions.html', transactions=transactions)


@app.route('/all')
def sorted_transactions_page():
    cursor = conn.cursor()
    cursor.execute("SELECT [cid], [BILLNO], [u_id], [a_id] FROM [backup for dbms].[dbo].[courier]")
    couriers = cursor.fetchall()

    # Fetch data from sender table
    cursor.execute("SELECT [BILLNO], [SNAME], [SEMAIL], [SPHONE], [SADDRESS] FROM [backup for dbms].[dbo].[Senders]")
    senders = cursor.fetchall()

    # Fetch data from receiver table
    cursor.execute("SELECT [BILLNO], [REMAIL], [RPHONE], [RADDRESS] FROM [backup for dbms].[dbo].[Receivers]")
    receivers = cursor.fetchall()

    # Fetch data from transactions table
    cursor.execute("SELECT [BILLNO], [DATE], [RNAME], [U_ID], [A_ID] FROM [backup for dbms].[dbo].[Transactions]")
    transactions = cursor.fetchall()

    # Merge data from all tables into a single list
    all_data = [('courier', *courier) for courier in couriers] + [('senders', *sender) for sender in senders] + [('receivers', *receiver) for receiver in receivers] + [('transactions', *transaction) for transaction in transactions]

    return render_template('all_info.html', all_data=all_data)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        comment = request.form['comment']
        rating = request.form['rating']

        cursor = conn.cursor()
        # Insert data into database
        cursor.execute("INSERT INTO [backup for dbms].[dbo].[comment] (email, comment, date, rating) VALUES (?, ?, GETDATE(), ?)",
                       (email, comment, rating))
        conn.commit()

    return render_template('contact.html')


@app.route('/ship', methods=['GET', 'POST'])
def render_ship_form():
    if request.method == 'POST':
        # This block would be used for processing form data, but since we're not doing that in this example,
        # we can simply redirect back to the ship.html page.
        return render_template('ship.html')

    # If the request method is GET, simply render the ship.html page.
    return render_template('ship.html')

    
@app.route('/track', methods=['GET'])
def track_shipment():
    # Assuming you have established a connection to your database
    cursor = conn.cursor()
    cursor.execute("SELECT [BILLNO], [status], [delivery_date] FROM [backup for dbms].[dbo].[track]")
    data = cursor.fetchall()
    return render_template('track.html', data=data)





if __name__ == "__main__":
    app.run(debug=True, port=8000)