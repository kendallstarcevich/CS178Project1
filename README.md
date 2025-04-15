# Project summary
My project is a Flask-based web application that allows users to view, search, and manage Airbnb listings and reviews from Seattle. The app connects to a MySQL database for listings and reviews and AWS DynamoDB for user data. It can be ran on your local machine or cloned onto an AWS EC2 instance. Mine is currently persistent on my EC2 instance at: [Live Application](http://34.238.151.33:8080/)

**Users can:**
- Sign up and log in
- Submit, view , and delete their own reviews
- View listings by price based on room type and neighborhood
- View reviews sorted by date of listings.
- Manage account - change password, see ID, logout, delete account

# Technologies used
- **Frontend**: HTML, CSS, Bootstrap, Jinja2 templating (all in templates folder)

- **Backend**: Python (Flask, in flaskapp.py file)

- **Database**: MySQL (AWS RDS) for Listings and Reviews, DynamoDB (AWS) for Users. (managed using Boto3 and SQL in dbCode.py)

- **Version Control**: Git and GitHub 


# Setup and run instructions

1. ### **Fork my repository**
2. ### **Set up RDS Database and EC2 Instance in AWS with the correct permissions**
3. ### **Install dependencies:** 
```pip install -r requirements.txt```
4. ### **Set up environment:** 
Make sure that the creds.py file contains the MySQL and DynamoDB credentials. Example structure for creds.py: 
```
python host = "your-rds-hostname"
user = "your-username"
password = "your-password"
db = "your-db-name"
```
5. ### **Create MySQL and DynamoDB tables:** 
The dataset I used to create my three MySQL tables were downloaded from [Kaggle Seattle Airbnb Data](https://www.kaggle.com/datasets/swsw1717/seatle-airbnb-open-data-sql-project?select=calendar.csv) These .csv files are in my .gitignore because they are too large to store here.

* *I cleaned out the calendar csv in the cleaning.py file to remove the $ in the price column and drop the adjusted_price columnn because it was empty*

###### MySQL: 
Navigate to MySQL shell by reconnecting to EC2 instance. Then run ```mysql -h your_rds_endpoint -u admin -p < airbnb.sql``` to create the database.

To populate the tables, use
```mysql -h your_rds_endpoint -u admin -p --local-infile```
and run: 

```
LOAD DATA LOCAL INFILE '/pathtocsv/listings.csv
INTO TABLE Listings
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```
*Repeat for Calendar and Reviews*

6. ### **Run the Flask app:** 
in the terminal in your working directory on your machine, run: ```python3 flaskapp.py``` and navigate to http://localhost:8080 in your browser or run the same thing in your EC2 instance and navigate to http://EC2host:8080/