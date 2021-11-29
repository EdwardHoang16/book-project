/*
    This file creates the books and credentials tables if they do not already exist.
*/

DROP TABLE IF EXISTS books;

CREATE TABLE books (
    bookID INTEGER PRIMARY KEY,
    title TEXT,
    authors TEXT,
    average_rating TEXT,
    isbn TEXT,
    isbn13 TEXT,
    language_code TEXT,
    num_pages TEXT,
    ratings_count TEXT,
    text_reviews_count TEXT,
    publication_date TEXT,
    publisher TEXT,
    renter TEXT
);


DROP TABLE IF EXISTS credentials;

CREATE TABLE credentials (
    email TEXT PRIMARY KEY,
    password TEXT
);
