from flask import Flask, render_template, request, session, redirect, url_for, flash
from dbCode import *
from datetime import date


app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/account')
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    reviewer_id = session['reviewer_id']
    return render_template('account.html', username=username, reviewer_id=reviewer_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/login', methods = ['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    user = user_login(table, username, password)

    if user:
        session['username'] = username
        session['reviewer_id'] = user['ID']
        return render_template('review.html')
    else:
        return render_template('login.html', error="❌ Invalid username or password.")


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    reviewer_id = create_user2(table, name, username, password)
    return render_template('signup_success.html', username=username, reviewer_id=reviewer_id)

@app.route('/change_password', methods=['GET'])
def change_password():
    return render_template('change_password.html')

@app.route('/change_password', methods=['POST'])
def change_password_post():
    new_password = request.form['new_password']

    success = update_password2(table, session['username'], new_password)
    if success:
        flash("✅ Password updated successfully.")
    else:
        flash("❌ Error updating password.")
    return redirect(url_for('account'))

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

@app.route("/reviews/<reviewer_id>")
def view_reviews(reviewer_id):
    rows = execute_query("""select r.review_id, r.review_date, l.host_name, l.name, l.neighbourhood, r.comments
from Listings l join Reviews r on l.id = r.listing_id
where r.reviewer_id = %s
order by r.review_date desc
limit 10""", (reviewer_id))
    return display_reviews(rows)

@app.route('/review')
def review_page():
    reviewer_id = session.get('reviewer_id')          
    return render_template('review.html', reviewer_id=reviewer_id)

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


@app.route('/add-review', methods=['GET', 'POST'])
def add_review():
    if request.method == 'POST':
        try:
            review_id = generate_unique_review_id()
            review_date = date.today().strftime('%Y-%m-%d')
            comments = request.form['comments']
            reviewer_id = session.get('reviewer_id')
            listing_id = request.form['listing_id']

            conn = get_conn()  # manually get the connection
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO Reviews (review_id, review_date, comments, reviewer_id, listing_id) VALUES (%s, %s, %s, %s, %s)",
                (review_id, review_date, comments, reviewer_id, listing_id)
            )
            conn.commit()  # ✅ explicitly commit

            cur.close()
            conn.close()

            flash("✅ Review submitted successfully!", "success")
            return redirect(url_for('account'))

        except Exception as e:
            print("Error inserting review:", e)
            flash("❌ Error submitting review.", "danger")
            return redirect(url_for('add_review'))

    return render_template('add_review.html')


@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")


@app.route("/pricequerytextbox", methods = ['POST'])
def price_form_post():
  text = request.form['text']
  return viewprices(text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

