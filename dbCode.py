import pymysql
import creds 

def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.password,
        db=creds.db,
        )
    return conn

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def display_html(rows):
    html = ""
    html += """<table border="1">
    <tr>
        <th>Listing ID</th>
        <th>Name</th>
        <th>Price</th>
        <th>Review Date</th>
        <th>Comment</th>
    </tr>"""

    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>${r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"

    html += "</table>"
    return html


def display_price(rows):
    html = ""
    html += """<table border="1">
    <tr>
        <th>Listing ID</th>
        <th>Price</th>
        <th>Neighborhood</th>
        <th>Room Type</th>
        <th>Available</th>
        <th>Minimum Nights</th>
        <th>Maximum Nights</th>
    </tr>"""

    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>${r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td></tr>"

    html += "</table>"
    return html
