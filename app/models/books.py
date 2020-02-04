import logging
from collections import Counter

from app.config import db
from app.models.book_tags import BookTags


class Books(db.Model): #the books table as a class where all the columns are identified 
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    book_id = db.Column(db.Integer)
    goodreads_book_id = db.Column(db.Integer)
    isbn13 = db.Column(db.Integer)
    authors = db.Column(db.String(200))
    original_publication_year = db.Column(db.Integer)
    original_title = db.Column(db.String(120))
    title = db.Column(db.String(400))
    language_code = db.Column(db.String(40))
    average_rating = db.Column(db.Float)
    ratings_count = db.Column(db.Integer)
    image_url = db.Column(db.String(200))


    @classmethod
    def get_paginated(cls, page):
        return cls.query.paginate(page, 12, False).items


    @classmethod
    def get_list(cls, ids):
        return cls.query.filter(cls.book_id.in_(ids))


    @classmethod
    def get_list_from_goodreads_ids(cls, ids):
        return cls.query.filter(cls.goodreads_book_id.in_(ids))


    @classmethod
    def get_book(cls, id):
        try:
            res = cls.query.filter_by(book_id=id).first()
            tags = BookTags.get_tags(res.__dict__.get("goodreads_book_id"), n=10)
            tag_names = [ x.get("tag_name") for x in tags ]
            res.__dict__["tags"] = tag_names

            if res is not None:
                return res.__dict__
            return None
        except Exception as e:
            logging.error(e)
            return None
