DROP TABLE IF EXISTS Attributes, Categories, Checkin, Review, Friendship, Users, Business, ZipcodeData CASCADE;

CREATE TABLE IF NOT EXISTS Users (
    user_id         VARCHAR(255) PRIMARY KEY,
    name            VARCHAR(255),
    yelping_since   DATE,
    review_count    INTEGER DEFAULT 0,
    fans            INTEGER DEFAULT 0,
    average_stars   FLOAT,
    funny           INTEGER DEFAULT 0,
    useful          INTEGER DEFAULT 0,
    cool            INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Friendship (
    user_id         VARCHAR(255),
    friend_id       VARCHAR(255),
    PRIMARY KEY (user_id, friend_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (friend_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Business (
    business_id     VARCHAR(255) PRIMARY KEY,
    name            VARCHAR(255),
    address         VARCHAR(255),
    city            VARCHAR(35),
    state           CHAR(2),
    zipcode         CHAR(5),
    review_count    INTEGER DEFAULT 0,
    stars           FLOAT,
    reviewrating    FLOAT DEFAULT 0.0,
    numCheckins     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Review (
    review_id       VARCHAR(255) PRIMARY KEY,
    business_id     VARCHAR(255),
    user_id         VARCHAR(255),
    stars           FLOAT,
    date            DATE,
    text            TEXT,
    useful_vote     INTEGER DEFAULT 0,
    funny_vote      INTEGER DEFAULT 0,
    cool_vote       INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE IF NOT EXISTS Checkin (
    business_id     VARCHAR(255),
    day             VARCHAR(10),
    time            VARCHAR(10),
    count           INTEGER DEFAULT 0,
    PRIMARY KEY (business_id, day, time),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE IF NOT EXISTS Categories (
    business_id     VARCHAR(255),
    category_name   VARCHAR(255),
    PRIMARY KEY (business_id, category_name),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE IF NOT EXISTS Attributes (
    business_id     VARCHAR(255),
    attr_name       VARCHAR(255),
    value           VARCHAR(255),
    PRIMARY KEY (business_id, attr_name),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE IF NOT EXISTS ZipcodeData (
    zipcode TEXT PRIMARY KEY,
    medianIncome INTEGER,
    meanIncome INTEGER,
    population INTEGER
);