from app.config import db
from uuid import uuid4
from passlib.hash import pbkdf2_sha256
from app.models.user_books import UserBooks
from app.models.books import Books


class EmailExistsError(Exception):
    """Raised when an email is already associated with an account"""

    pass


class UserDoesNotExistError(Exception):
    """Raised when an account with given email does not exist"""

    pass


class PasswordTooShortError(Exception):
    """Raised when the password is shorter than 10 characters long"""

    pass


def member_token():
    """Returns a random string of length string_length."""
    return uuid4().hex


def salt_and_hash(password):
    return pbkdf2_sha256.hash(password)


def verify_password(password, hash):
    return pbkdf2_sha256.verify(password, hash)


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.String(120), primary_key=True, unique=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    pwd = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean)

    def __init__(self, name=None, email=None, password=None, is_admin=False):
        self.user_id = member_token()
        self.name = name
        self.email = email
        self.pwd = password
        self.is_admin = is_admin

    def __repr__(self):
        return "email: {0},\n is_admin: {1}".format(self.email, self.is_admin)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.name)

    def get_name(self):
        return self.name

    def get_books(self):
        book_obj_lst = UserBooks.get_books(user_id=self.user_id)
        bmap = {b.get("book_id"): b for b in book_obj_lst}
        books = Books.get_list(ids=[b.get("book_id") for b in book_obj_lst])
        res = []
        for b in books:
            b.__dict__["reading_state"] = bmap[b.__dict__["book_id"]]["reading_state"]
            res.append(b.__dict__)
        return res

    @classmethod
    def verify_user(cls, email, password):
        u = cls.query.filter_by(email=email).first()
        if u is not None:
            if verify_password(password, u.pwd):
                return u
        return None

    @classmethod
    def register(cls, name, email, is_admin, password=None):
        try:
            existing = cls.query.filter_by(email=email).first()
            if existing:
                raise EmailExistsError
            if password is None or len(password) < 8:
                raise PasswordTooShortError

            hashed_password = salt_and_hash(password)
            u = User(
                name=name, email=email, password=hashed_password, is_admin=is_admin
            )
            db.session.add(u)
            db.session.commit()
            return cls.query.filter_by(email=email).first()
        except Exception as e:
            raise e

    @classmethod
    def update_password(cls, email, password=None):
        try:
            if password is None:
                return Exception
            u = cls.query.filter_by(email=email).first()
            hashed_password = salt_and_hash(password)
            u.pwd = hashed_password
            db.session.add(u)
            db.session.commit()
            return cls.query.filter_by(email=email).first()
        except Exception as e:
            print(e)
            return None

    @classmethod
    def update(cls, user_email, **kwargs):
        u = cls.query.filter_by(email=user_email).first()
        if not u:
            raise UserDoesNotExistError

        if kwargs.get("email"):
            print("Updating email: ", kwargs.get("email"))
            u.email = kwargs.get("email")
        if kwargs.get("name"):
            print("Updating name: ", kwargs.get("name"))
            u.name = kwargs.get("name")
        if kwargs.get("password"):
            print("Updating password: ", kwargs.get("password"))
            u.pwd = salt_and_hash(kwargs.get("password"))
        if kwargs.get("is_admin"):
            print("Updating is_admin: ", kwargs.get("is_admin"))
            u.is_admin = kwargs.get("is_admin")

        db.session.add(u)
        db.session.commit()
        return True

    @classmethod
    def update_password(cls, email, password):
        u = cls.query.filter_by(email=email).first()
        u.pwd = salt_and_hash(password)
        db.session.add(u)
        db.session.commit()
        return True

    @classmethod
    def update_email(cls, old_email, email):
        u = cls.query.filter_by(email=old_email).first()
        email_is_taken = cls.query.filter_by(email=email).first()
        if email_is_taken:
            raise EmailExistsError

        u.email = email
        db.session.add(u)
        db.session.commit()
        return True

    @classmethod
    def update_name(cls, email, name):
        u = cls.query.filter_by(email=email).first()
        u.name = name
        db.session.add(u)
        db.session.commit()
        return True

    @classmethod
    def delete(cls, email):
        if email is not None:
            u = cls.query.filter_by(email=email).first()
            db.session.delete(u)
            db.session.commit()
            return True
        return False
