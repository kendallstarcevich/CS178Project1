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
    """Display the account page with user information."""
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    reviewer_id = session['reviewer_id']
    return render_template('account.html', username=username, reviewer_id=reviewer_id)

@app.route('/delete-review', methods=['GET', 'POST'])
def delete_review():
    """Delete a review from the database."""
    if 'reviewer_id' not in session:
        return redirect(url_for('login'))

    reviewer_id = session['reviewer_id']

    if request.method == 'POST':
        review_id = request.form['review_id']
        confirm = request.form.get('confirm')

        if confirm == 'yes':

            #CHATGPT HELPED WITH MANUALLY GETTING THE CONNECTION (I could not figure out how to actually change the table)
            conn = get_conn()  # manually get the connection
            cur = conn.cursor()

            cur.execute("DELETE FROM Reviews WHERE review_id = %s", (review_id,))
            conn.commit()  # ✅ explicitly commit
            cur.close()
            conn.close()

            flash("✅ Review deleted successfully!", "success")
            return redirect(url_for('my_reviews'))

    reviews = execute_query(
        "SELECT review_id, comments FROM Reviews WHERE reviewer_id = %s ORDER BY review_date DESC",
        (reviewer_id,)
    )
    return render_template('delete_review.html', reviews=reviews)

@app.route('/logout')
def logout():
    """clears the session data so that you can log in with a different user"""
    session.clear()
    return redirect(url_for('home'))


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
        return redirect(url_for('account'))
    else:
        return render_template('login.html', error="❌ Invalid username or password.")


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    """Creates an entry in the Users table"""
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


@app.route('/confirm_delete', methods=['GET'])
def delete_user_confirm():
    #I wanted to make a confirmation page before deleting the user so that they don't accidentally delete their account
    username = session.get('username')
    if not username:
        flash("You must be logged in to delete your account.", "danger")
        return redirect(url_for('login'))
    return render_template('confirm_delete.html', username=username)

@app.route('/confirm_delete', methods=['POST'])
def delete_user_post():
    username = session.get('username')
    if not username:
        flash("No user found in session.", "danger")
        return redirect(url_for('login'))

    try:
        table.delete_item(
            Key={'Username': username}
        )
        session.clear() 
        flash("✅ Your account has been successfully deleted.", "success")
        return redirect(url_for('login'))
    except Exception as e:
        print("Error deleting user:", e)
        flash("❌ There was a problem deleting your account.", "danger")
        return redirect(url_for('account'))

@app.route('/about')
def about():
    """Display the about page - it talks about the project"""
    return render_template('about.html')

@app.route("/reviews/<reviewer_id>")
def view_reviews(reviewer_id):
    """Display the reviews for a specific reviewer."""
    rows = execute_query("""select r.review_id, r.review_date, l.host_name, l.name, l.neighbourhood, r.comments
from Listings l join Reviews r on l.id = r.listing_id
where r.reviewer_id = %s
order by r.review_date desc
limit 10""", (reviewer_id))
    return display_reviews(rows)

@app.route("/my_reviews")
def my_reviews():
    """Display the reviews for the logged-in user."""
    if 'reviewer_id' not in session:
        return redirect(url_for('login'))  # safety check
    reviewer_id = session['reviewer_id']

    rows = execute_query("""
        SELECT r.review_id, r.review_date, l.host_name, l.name, l.neighbourhood, r.comments
        FROM Listings l
        JOIN Reviews r ON l.id = r.listing_id
        WHERE r.reviewer_id = %s
        ORDER BY r.review_date DESC
        LIMIT 10
    """, (reviewer_id,))

    return render_template("my_reviews.html", reviews=rows, reviewer_id=reviewer_id)


@app.route('/review')
def review_page():
    """Display the review page. This is where the user can add or view reviews"""
    reviewer_id = session.get('reviewer_id')          
    return render_template('review.html', reviewer_id=reviewer_id)


@app.route('/add-review', methods=['GET', 'POST'])
def add_review():
    if request.method == 'POST':
        try:
            review_id = generate_unique_review_id()
            review_date = date.today().strftime('%Y-%m-%d')
            comments = request.form['comments']
            reviewer_id = session.get('reviewer_id')
            listing_id = request.form['listing_id']

            #CHATGPT HELPED WITH MANUALLY GETTING THE CONNECTION (I could not figure out how to actually change the table)
            conn = get_conn()  
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO Reviews (review_id, review_date, comments, reviewer_id, listing_id) VALUES (%s, %s, %s, %s, %s)",
                (review_id, review_date, comments, reviewer_id, listing_id)
            )
            conn.commit() 

            cur.close()
            conn.close()

            flash("✅ Review submitted successfully!", "success")
            return redirect(url_for('my_reviews'))

        except Exception as e:
            print("Error inserting review:", e)
            flash("❌ Error submitting review.", "danger")
            return redirect(url_for('add_review'))

    return render_template('add_review.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Display the search page and handle search queries."""
    if request.method == 'POST':
        selected_room_type = request.form['room_type']
        selected_neighbourhood = request.form['neighbourhood']

        listings = execute_query(
            """
            SELECT c.listing_id, c.price, l.room_type, l.neighbourhood, l.name
            FROM Listings l
            JOIN Calendar c ON l.id = c.listing_id
            WHERE l.room_type = %s AND l.neighbourhood = %s
            GROUP BY c.listing_id
            ORDER BY c.price ASC
            LIMIT 100;
            """,
            (selected_room_type, selected_neighbourhood)
        )

        return render_template(
            'search.html',
            listings=listings,
            selected_room_type=selected_room_type,
            selected_neighbourhood=selected_neighbourhood
        )

    #Chat GPT helped me get the dropdowns to work
    room_types = [row[0] for row in execute_query("SELECT DISTINCT room_type FROM Listings;")]
    neighbourhoods = [row[0] for row in execute_query("SELECT DISTINCT neighbourhood FROM Listings;")]

    return render_template('search.html', room_types=room_types, neighbourhoods=neighbourhoods)

@app.route('/review_search', methods=['GET', 'POST'])
def review_search():
    """Display the review search page and handle search queries."""
    listings = []
    if request.method == 'POST':

        listing_id = request.form['listing_id']
        listings = execute_query(
            """
           select review_date, reviewer_name, comments
            from Reviews
            where listing_id = %s
            order by review_date desc
            limit 100
            """,
            (listing_id,)
        )

        return render_template(
            'review_search.html',
            listings=listings,
            listing_id=listing_id
        )

    return render_template('review_search.html', listings = listings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

