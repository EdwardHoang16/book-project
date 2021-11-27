import pandas as pd
import sqlite3

connection = sqlite3.connect('database.db')

with open('books.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()


# filePath = "/Users/ayushmaheshwari/sjsu/cs122/book-project/books.csv"
filePath = "./books.csv"
bookID = []
title = []
authors = []
average_rating = []
isbn = []
isbn13 = []
language_code = []
num_pages = []
ratings_count = []
text_reviews_count = []
publication_date = []
publisher = []
renter = []
j = 0
with open(filePath, "r") as a_file:
    for line in a_file:
        if j == 0:
            j = j + 1
            continue
        i = 0
        for s in line.split(","):
            if i == 0:
                bookID.append(s)
            elif i == 1:
                title.append(s)
            elif i == 2:
                authors.append(s)
            elif i == 3:
                average_rating.append(s)
            elif i == 4:
                isbn.append(s)
            elif i == 5:
                isbn13.append(s)
            elif i == 6:
                language_code.append(s)
            elif i == 7:
                num_pages.append(s)
            elif i == 8:
                ratings_count.append(s)
            elif i == 9:
                text_reviews_count.append(s)
            elif i == 10:
                publication_date.append(s)
            elif i == 11:
                publisher.append(s[:len(s) - 1])
            i = i + 1
        renter.append("")

df = pd.DataFrame(
        {'bookID': bookID, 'title': title, 'authors': authors, 'average_rating': average_rating, 'isbn': isbn,
         'isbn13': isbn13, 'language_code': language_code, 'num_pages': num_pages, 'ratings_count': ratings_count,
         'text_reviews_count': text_reviews_count, 'publication_date': publication_date, 'publisher': publisher,
        'renter': renter})

df.to_sql('books', connection, if_exists='append', index=False)
connection.commit()
connection.close()

