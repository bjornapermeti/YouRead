import pandas as pd
import sqlite3
#The helpers.py file is helper module that takes multiple csv files, run basic pre-processing and creates SQL tables in our database from the csv files.

# Sanitize some of the not-so-useful tags, this are the tags which are found in the database but we are not going to use in our project
#Remove this tags from the data
blacklist_tags = set(
    [
        "to-read",
        "favorites",
        "favourites",
        "books-i-own",
        "owned",
        "currently-reading",
        "read",
        "want-to-read",
        "on-hold",
        "ya",
        "read-in-2015",
        "read-in-2014",
        "read-2013",
        "read-in-2009",
        "i-own-it",
        "2016-reads",
    ]
)

#This are the tags that the book columns will contain

book_columns = [
    "book_id",
    "goodreads_book_id",
    "isbn13",
    "authors",
    "original_publication_year",
    "original_title",
    "title",
    "language_code",
    "average_rating",
    "ratings_count",
    "image_url",
]


# Function to decice whether or not a particular tag
# will be added to the production database
def show_tag(tag_frequency, tag): 
    global blacklist_tags 
    #it checks if the tags are in the blacklist or if they are not used that often with a minimum with 20
    #if one of this conditions is met than the tag is not shown it will return false
    if tag in blacklist_tags or tag_frequency[tag] < 20 or len(tag) < 5: 
        return False
    return True


def populate_db(dbpath, datapath):

    connex = sqlite3.connect(str(dbpath.joinpath("app.db"))) #connects to the application database
    # This object lets us actually send messages to our DB and receive results
    cur = connex.cursor()

    books = pd.read_csv(datapath.joinpath("books.csv")) #the books dataset are stored in a csv file
    books = books[book_columns]  # keep only desired columns

    book_tags = pd.read_csv(datapath.joinpath("book_tags.csv"))
    tags = pd.read_csv(datapath.joinpath("tags.csv"))
    similar_books = pd.read_csv(datapath.joinpath("similar_books.csv"))

    # Merge tag names into book_tags, the split is redundant
    book_tags = pd.merge(
        book_tags, tags, left_on="tag_id", right_on="tag_id", how="inner"
    )

    # calculate how on how many books a particular tag_name appears
    tag_frequency = book_tags.tag_name.value_counts()

    book_tags["show"] = book_tags.tag_name.apply(
        lambda tag: show_tag(tag_frequency, tag)
    )
    book_tags = book_tags[book_tags.show == True]
    book_tags = book_tags[["goodreads_book_id", "tag_id", "count", "tag_name"]]

    # Write to DB
    books.to_sql(name="books", con=connex, if_exists="append", index=False) 
    book_tags.to_sql(
        name="book_tags", con=connex, if_exists="append", index=True, index_label="id"
    )
    similar_books.to_sql(
        name="similar_books",
        con=connex,
        if_exists="append",
        index=False,
        index_label="id",
    )
