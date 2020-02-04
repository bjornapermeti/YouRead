from app.config import db
import time


class UserBooks(db.Model):
    __tablename__ = "user_books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    user_id = db.Column(db.Integer)
    book_id = db.Column(db.Integer)
    time = db.Column(db.Integer)
    reading_state = db.Column(db.Integer)

    reading_state_repr = {
        0: 'Want to read',
        1: 'Currently reading',
        2: 'Read'
    }

    @classmethod
    def get_books(cls, user_id):
        """Gets list of tags for a given book.

        Args:
            user_id ([string]): Goodreads book id provided in the dataset.
                            Encountered as `goodreads_book_id`

        Returns:
            [List]: List of book_ids
        """
        return [
            x.__dict__
            for x in (
                cls.query
                .filter_by(user_id=user_id)
                .order_by(cls.time.desc())
            )
        ]

    @classmethod
    def add_entry(cls, user_id, book_id, reading_state):
        try:
            assert reading_state in cls.reading_state_repr.keys()

            user_book_pair = (
                cls.query
                .filter_by(user_id=user_id)
                .filter_by(book_id=book_id)
                .first()
            )
            if user_book_pair:
                if user_book_pair.reading_state == reading_state:
                    pass
                else:
                    user_book_pair.reading_state = reading_state
                    user_book_pair.time = int(time.time())
            else:
                ub = UserBooks(
                    user_id=user_id,
                    book_id=book_id,
                    time=int(time.time()),
                    reading_state=reading_state
                )
                db.session.add(ub)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_reading_state(cls, user_id, book_id):
        user_book_pair = (
            cls.query
            .filter_by(user_id=user_id)
            .filter_by(book_id=book_id)
            .first()
        )
        if user_book_pair:
            return user_book_pair.__dict__.get("reading_state", 0)
        return None
