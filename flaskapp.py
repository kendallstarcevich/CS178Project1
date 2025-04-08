from flask import Flask
from flask import render_template
from dbCode import *

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h2>Hello from Flask Project 1!</h2>'

@app.route('/about')
def about():
    return '<h2>An about page!</h2>'

@app.route('/hello/<username>/')
def hello_user(username):
    return render_template('layout.html', name=username)

@app.route('/repeat/<var>')
def repeater(var):
    result=""
    for i in range(10):
        result += var
    return result

@app.route("/numchar/<var>")
def numchar(var):
    result=""
    result = len(var)
    result = str(result)
    return result
    

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


@app.route("/timequery/<time>")
def viewtime(time):
    rows = execute_query("""SELECT ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
                FROM Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
                where Milliseconds > %s order by Track.Name 
                Limit 500""", (str(time)))
    return display_html(rows)


from flask import request


@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")


@app.route("/pricequerytextbox", methods = ['POST'])
def price_form_post():
  text = request.form['text']
  return viewprices(text)


@app.route("/timequerytextbox", methods = ['GET'])
def time_form():
  return render_template('textbox.html', fieldname = "Time")

@app.route("/timequerytextbox", methods = ['POST'])
def time_form_post():
  text = request.form['text']
  return viewtime(text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

