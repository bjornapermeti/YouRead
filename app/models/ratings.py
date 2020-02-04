from app.config import db


class Ratings(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    user_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)
