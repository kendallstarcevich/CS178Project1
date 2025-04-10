from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import *


app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/login', methods = ['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    if user_login(table, username, password):
        return redirect(url_for('account'))
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('login'))


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    reviewer_id = create_user2(table, name, username, password)

    return f"<h2>✅ Account created! Your Reviewer ID is: {reviewer_id}. You can now <a href='/login'>log in</a>.</h2>"


@app.route('/about')
def about():
    return '<h2>An about page!</h2>'

@app.route('/hello/<username>/')
def hello_user(username):
    return render_template('layout.html', name=username)

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT l.id, l.name, l.price, r.review_date, r.comments
        FROM Listings l
        JOIN Reviews r ON l.id = r.listing_id
        LIMIT 10
""")
    return display_html(rows)


@app.route("/pricequery/<price>")
def viewprices(price):
    rows = execute_query("""
        SELECT 
    c.listing_id,
    c.price,
    l.neighbourhood,
    l.room_type,
    c.minimum_nights,
    c.maximum_nights
FROM Listings l
JOIN Calendar c ON l.id = c.listing_id
WHERE c.price = %s
GROUP BY c.listing_id, l.neighbourhood, l.room_type
LIMIT 10
    """, (price,))
    return display_price(rows)


@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")


@app.route("/pricequerytextbox", methods = ['POST'])
def price_form_post():
  text = request.form['text']
  return viewprices(text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

