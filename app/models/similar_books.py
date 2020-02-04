from app.config import db


class SimilarBooks(db.Model):
    __tablename__ = "similar_books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    goodreads_book_id = db.Column(db.Integer)
    sim_goodreads_book_id = db.Column(db.Integer)

    @classmethod
    def get_sim_ids(cls, gid):
        """Gets list of similar book_ids for a given book.

        Args:
            gid ([string]): Goodreads book id provided in the dataset.
                            Encountered as `goodreads_book_id`

        Returns:
            [List]: List of ids
        """
        return [
            x.__dict__.get("sim_goodreads_book_id")
            for x in cls.query.filter_by(goodreads_book_id=gid)
        ]
