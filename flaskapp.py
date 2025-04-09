from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import *


app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('home.html')


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
        SELECT DISTINCT c.listing_id, c.price, l.neighbourhood, l.room_type, 
                        c.available, c.minimum_nights, c.maximum_nights 
        FROM Listings l
        JOIN Calendar c ON l.id = c.listing_id
        WHERE c.price = %s
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


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        genre = request.form['genre']
        
        # Process the data (e.g., add it to a database)
        # For now, let's just print it to the console
        print("Name:", name, ":", "Favorite Genre:", genre)
        
        flash('User added successfully!', 'success')  # 'success' is a category; makes a green banner at the top
        # Redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # Render the form page if the request method is GET
        return render_template('add_user.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

