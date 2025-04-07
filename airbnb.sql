-- Create the database
CREATE DATABASE IF NOT EXISTS AirbnbSeattle;
USE AirbnbSeattle;

-- Create the Listings table
CREATE TABLE Listings (
    id INT PRIMARY KEY,
    name TEXT,
    host_id INT,
    host_name VARCHAR(255),
    neighbourhood_group VARCHAR(255),
    neighbourhood VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    room_type VARCHAR(100),
    price FLOAT,
    minimum_nights INT,
    number_of_reviews INT,
    last_review DATE,
    reviews_per_month FLOAT,
    calculated_host_listings_count INT,
    availability_365 INT,
    number_of_reviews_ltm INT,
    license VARCHAR(100)
);

-- Create the Calendar table (adjusted_price REMOVED)
CREATE TABLE Calendar (
    listing_id INT,
    calendar_date DATE,
    available VARCHAR(5),
    price FLOAT,
    minimum_nights INT,
    maximum_nights INT,
    FOREIGN KEY (listing_id) REFERENCES Listings(id)
);

-- Create the Reviews table
CREATE TABLE Reviews (
    listing_id INT,
    review_id INT PRIMARY KEY,
    review_date DATE,
    reviewer_id INT,
    reviewer_name VARCHAR(255),
    comments TEXT,
    FOREIGN KEY (listing_id) REFERENCES Listings(id)
);
