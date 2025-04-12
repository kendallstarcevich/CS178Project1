import pymysql
import creds
import boto3
import random
from boto3.dynamodb.conditions import Attr

TABLE_NAME = "Users"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

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

def generate_unique_review_id():
    while True:
        review_id = str(random.randint(1000, 999999999))
        # Check MySQL to see if review_id already exists 
        result = execute_query(
            "SELECT COUNT(*) FROM Reviews WHERE review_id = %s",
            (review_id,)
        )
        if result[0][0] == 0:
            return review_id  # ✅ It's unique, return it!

def print_user(user_dict):
    # print out the values of the user dictionary
    print("Username: ", user_dict["Username"])
    print("Password: ", user_dict["Password"])
    print("Name: ", user_dict["Name"])
    print("ID: ", user_dict.get("ID"))
    print()

def print_all_users():
    response = table.scan() #get all of the users
    for user in response["Items"]:
        print_user(user)

def generate_unique_reviewer_id():
    while True:
        reviewer_id = str(random.randint(10000, 999999999))  # 5-9 digit number
        # Check MySQL to see if reviewer_id already exists 
        result = execute_query(
            "SELECT COUNT(*) FROM Reviews WHERE reviewer_id = %s",
            (reviewer_id,)
        )
        if result[0][0] == 0:
            # Check DynamoDB to see if reviewer_id already exists there (in case a user has not made a review)
            response = table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('ID').eq(reviewer_id),
                ProjectionExpression='ID')
            if len(response['Items']) == 0:
                return reviewer_id  # ✅ It's unique, return it!


def create_user(table):
    """
    prompt user for a username, password, name, and it will generate a random ID to add to the database
    """
    print("creating a user")
    name = input("Enter your first name: ")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    id = generate_unique_reviewer_id()
    table.put_item(
    Item={
            'Username': username,
            'Password': password,
            'Name': name,
            'ID': id
        }
    )
    print("Your account has been created. Your ID is: ", id)


def create_user2(table, name, username, password):
    """
    Accept form inputs to create a user from Flask
    """
    reviewer_id = generate_unique_reviewer_id()
    table.put_item(
        Item={
            'Username': username,
            'Password': password,
            'Name': name,
            'ID': reviewer_id
        }
    )
    return reviewer_id

def user_login(table, username, password):
    """
    Check if the username and password match a user in DynamoDB.
    Returns the user record if valid, otherwise None.
    """
    response = table.get_item(
        Key={'Username': username}
    )

    user = response.get('Item')
    if user and user['Password'] == password:
        return user  # ✅ Login successful
    else:
        return None  # ❌ Login failed


def update_password(table):
    """
    prompt user for a username
    have them change their password
    """
    print("updating user")

    try: 
        username=input("What is your username?: ")
        new_password = input("What would you like your new password to be?: ")
        table.update_item(
                Key = {"Username": username}, 
                UpdateExpression = "SET Password = :p", ExpressionAttributeValues = {':p': new_password}
            )
        print("Your password has been updated.")
    except Exception:
        print("Error in updating password.\n")

def update_password2(table, username, new_password):
    """
    Update the user's password in DynamoDB.
    """
    try:
        table.update_item(
            Key={"Username": username},
            UpdateExpression="SET Password = :p",
            ExpressionAttributeValues={':p': new_password}
        )
        return True  # ✅ Success
    except Exception as e:
        print("Error updating password:", str(e))
        return False  # ❌ Failure


def delete_user(table):
    """
    prompt user for a username
    delete user from the database
    """
    print("deleting user")

    try:
        username=input("What is the username? ")
        table.delete_item(
        Key={
            'Username': username
            } 
    )
        print("User has been deleted.")
    except Exception:
        print("Username not found.\n")

def query_id(table):
    """
    prompt user for the username
    print out their id
    """
    print("find id")
    username=input("What is the users username? ")
    response = table.get_item(
        Key={
            'Username': username
        }
    )
    try:
        user = response.get("Item")
        id = user["ID"]
        print(username,"'s ID is: ",id)

    except Exception:
        print("Username not found.")


def print_menu():
    print("----------------------------")
    print("Press C: to CREATE a new user")
    print("Press R: to READ all users")
    print("Press U: to UPDATE your password")
    print("Press D: to DELETE a user")
    print("Press Q: to QUERY the user's ID")
    print("Press X: to EXIT application")
    print("----------------------------")


def main():
    import boto3

    TABLE_NAME = "Users"

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(TABLE_NAME)

    input_char = ""
    while input_char.upper() != "X":
        print_menu()
        input_char = input("Choice: ")
        if input_char.upper() == "C":
            create_user(table)
        elif input_char.upper() == "R":
            print_all_users()
        elif input_char.upper() == "U":
            update_password(table)
        elif input_char.upper() == "D":
            delete_user(table)
        elif input_char.upper() == "Q":
            query_id(table)
        elif input_char.upper() == "X":
            print("exiting...")
        else:
            print('Not a valid option. Try again.')

#UNCOMMENT THIS IF YOU WANT TO SEE CRUD MENU
#main()


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
        <th>Minimum Nights</th>
        <th>Maximum Nights</th>
    </tr>"""

    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>${r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"

    html += "</table>"
    return html



def display_reviews(rows):
    html = ""
    html += """<table border="1">
    <tr>
        <th>Review ID</th>
        <th>Review Date</th>
        <th>Host Name</th>
        <th>Name of Listing</th>
        <th>Neighborhood</th>
        <th>Review</th>
    </tr>"""

    for r in rows:
        html += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td></tr>"

    html += "</table>"
    return html


