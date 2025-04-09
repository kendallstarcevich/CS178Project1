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

def print_all_actors(table):
    """
    display all actors in database
    """
    print("display all actors")
    print()

    def print_actors(actor_dict):
    # print out the values of the actor dictionary
        print("Name: ", actor_dict["Name"])
        print(" Age: ", actor_dict["Age"])
        print(" Movies: ", end="")
        for movie in actor_dict["Movies"]:
            print(movie,"|", end=" ")
        print()
        print(" Shows: ", end="")
        for show in actor_dict["Shows"]:
            print(show,"|", end=" ")
        
        print()
        print()

    response = table.scan() #get all of the actors
    for actor in response["Items"]:
        print_actors(actor)


def update_projects(table):
    """
    prompt user for an actor name
    promt user for a project (movie or show)
    update (add) project to the database
    """
    print("updating projects")

    try: 
        name=input("What is the actor's name? ")
        type = str(input("Enter M to add a Movie or S to add a Show: ")).upper()
        if type == "M":
            project = input("What is the name of the movie: ")
            table.update_item(
                Key = {"Name": name}, 
                UpdateExpression = "SET Movies = list_append(Movies, :m)", ExpressionAttributeValues = {':m': [project],}
            )
        if type == "S":
            project = input("What is the name of the show: ")
            table.update_item(
                Key = {"Name": name}, 
                UpdateExpression = "SET Shows = list_append(Shows, :s)", ExpressionAttributeValues = {':s': [project],}
            )
        else:
            print("Invalid input. Try again.")    

    except Exception:
        print("Error in updating projects.\n")

def delete_actor(table):
    """
    prompt user for an actor name
    delete item from the database
    """
    print("deleting actor")

    
    name=input("What is the actor's name? ")
    table.delete_item(
    Key={
        'Name': name
        }
    
)


def query_actors(table):
    """
    prompt user for the actor's name
    print out the age of the actor
    """
    print("query actor")
    name=input("What is the actor's name? ")
    response = table.get_item(
        Key={
            'Name': name
        }
    )
    try:
        actor = response.get("Item")
        age = actor["Age"]
        print("The actor is", age, "years old.")

    except Exception:
        print("Actor not found.")


def print_menu():
    print("----------------------------")
    print("Press C: to CREATE a new user")
    print("Press R: to READ all users")
    print("Press U: to UPDATE a user")
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
            update_projects(table)
        elif input_char.upper() == "D":
            delete_actor(table)
        elif input_char.upper() == "Q":
            query_actors(table)
        elif input_char.upper() == "X":
            print("exiting...")
        else:
            print('Not a valid option. Try again.')
main()


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
