#main.py is the entry point to the app source code
#here we define the routes in the web app
import os
import pathlib
import logging
import json

from flask import render_template, request, redirect, url_for, jsonify, Markup
import flask_login
import humanize
import numpy as np
import pandas as pd

from app.config import app, db
from app.models.users import User, EmailExistsError, PasswordTooShortError
from app.models.books import Books
from app.models.user_books import UserBooks
from app.models.similar_books import SimilarBooks
from app.utils.notifications import Notifications  
from app.utils.forms import (
    SignupForm,
    LoginForm,
    EditAccountForm,
    UpdatePasswordForm,
    UpdateEmailForm,
    UpdateNameForm,
) 


@app.template_filter("humanize_number")
def humanize_number(number):
    """Convert a number to a more human readable representation."""
    if len(str(number)) > 6:
        return humanize.intword(number)
    return humanize.intcomma(number)


@app.template_filter("first_letter")
def first_letter(str):
    """Convert a number to a more human readable representation."""
    if len(str) > 0:
        return str[0]
    return ""


@app.template_filter("capitalize")
def capitalize(str):
    return str.capitalize()


@app.template_filter("edit_user_acc")
def edit_user_acc(path):
    """Convert a number to a more human readable representation."""
    if "admin/account/edit/" in path and "@" in path:
        return True
    return False


# USER SESSIONS
# ----------------------------------------------------------------------------#
logging.basicConfig(level=logging.INFO)


# LOGIN
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

login_required = flask_login.login_required
login_user = flask_login.login_user

logout_user = flask_login.logout_user
current_user = flask_login.current_user


@login_manager.user_loader
def load_user(name):
    return User.query.filter_by(name=name).first()


# ----------------------------------------------------------------------------#
# ROUTES
# ----------------------------------------------------------------------------#
@app.route("/", methods=["GET"])
def home():
    if current_user.is_anonymous:
        page = request.args.get("page", 1, type=int)
        books = Books.get_paginated(page=page)
        return render_template(
            "pages/home.html", form=SignupForm(request.form), books=books
        )
    else:
        return redirect(url_for("profile"))


@app.route("/explore", methods=["GET"])
def explore():
    page = request.args.get("page", 1, type=int)
    books = Books.get_paginated(page=page)
    return render_template(
        "pages/home.html", form=SignupForm(request.form), books=books
    )


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")

        # verify credentials
        res = User.verify_user(email, password)
        if res is not None:
            login_user(res)
            return redirect(url_for("home"))
        Notifications.info_bad_login()

    # if form data fails validation, head back to home
    return redirect(url_for("home"))


# PROFILE and ACCOUNT routes
# ----------------------------------------------------------------------------#
@app.route("/profile", methods=["GET"])
@login_required
def profile():
    books = current_user.get_books()
    want_to_read = []
    currently_reading = []
    read = []
    for b in books:
        if b.get("reading_state") == 0:
            want_to_read.append(b)
        elif b.get("reading_state") == 1:
            currently_reading.append(b)
        elif b.get("reading_state") == 2:
            read.append(b)

    return render_template(
        "pages/profile.html",
        books=books,
        want_to_read=want_to_read[:4],
        currently_reading=currently_reading[:4],
        read=read[:4],
    )


@app.route("/profile/want_to_read", methods=["GET"])
@login_required
def want_to_read():
    books = [b for b in current_user.get_books() if b.get("reading_state") == 0]
    return render_template("pages/profile.html", books=books)


@app.route("/profile/currently_reading", methods=["GET"])
@login_required
def currently_reading():
    books = [b for b in current_user.get_books() if b.get("reading_state") == 1]
    return render_template("pages/profile.html", books=books)


@app.route("/profile/read", methods=["GET"])
@login_required
def read():
    books = [b for b in current_user.get_books() if b.get("reading_state") == 2]
    return render_template("pages/profile.html", books=books)


@app.route("/follow/book", methods=["POST"])
@login_required
def add_book():
    payload = json.loads(request.data.decode("utf-8"))
    added = UserBooks.add_entry(
        user_id=current_user.user_id,
        book_id=payload.get("book_id"),
        reading_state=payload.get("readingState"),
    )
    if added:
        return jsonify(success=True)
    return jsonify(success=False)


@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    is_admin = request.form.get("is_admin", False)

    # register user to db
    try:
        new_user = User.register(name, email, is_admin, password)
        if new_user is None:
            Notifications.info_try_again()

        if not current_user.is_anonymous:
            if current_user.is_admin:
                Notifications.info_account_created(name, password, email)
                return redirect(url_for("admin"))
        else:
            # Login the user
            u = User.verify_user(email, password)
            login_user(u)
            Notifications.info_account_created(name, password, email)
            return redirect(url_for("home"))
    except EmailExistsError:
        Notifications.email_exists(email)
    except PasswordTooShortError:
        Notifications.password_too_short()
    return redirect(url_for("home"))


@app.route("/account/update_email", methods=["GET", "POST"])
@login_required
def update_email():
    if request.method == "GET":
        user = User.query.filter_by(email=current_user.email).first()
        return render_template("pages/account.html", form=UpdateEmailForm(), user=user)

    # If user is admin
    if request.method == "POST":
        form = UpdateEmailForm(request.form)
        if form.validate_on_submit():
            verified = User.verify_user(current_user.email, form.data.get("password"))
            if verified:
                # TODO: Handle condition for uniqueness
                try:
                    updated = User.update_email(
                        old_email=current_user.email, email=form.data.get("email")
                    )
                    if updated:
                        Notifications.info_account_updated(**form.data)
                        login_user(current_user)
                        return redirect(url_for("account"))
                except EmailExistsError:
                    Notifications.email_exists(form.data.get("email"))
                    return redirect(url_for("update_email"))

        Notifications.info_try_again()
        return redirect(url_for("update_email"))



@app.route("/account/update_name", methods=["GET", "POST"])
@login_required
def update_name():
    # If user is admin
    if request.method == "POST":
        form = UpdateNameForm(request.form)
        if form.validate_on_submit():
            verified = User.verify_user(current_user.email, form.data.get("password"))
            print("verified: ", verified)
            if verified:
                updated = User.update_name(
                    email=current_user.email, name=form.data.get("name")
                )
                if updated:
                    Notifications.info_account_updated(**form.data)
                    login_user(current_user)
                    return redirect(url_for("account"))

        Notifications.info_try_again()
        return redirect(url_for("update_email"))

    elif request.method == "GET":
        user = User.query.filter_by(email=current_user.email).first()
        return render_template("pages/account.html", form=UpdateNameForm(), user=user)


@app.route("/account/update_password", methods=["GET", "POST"])
@login_required
def update_password():
    if request.method == "GET":
        user = User.query.filter_by(email=current_user.email).first()
        return render_template(
            "pages/account.html", form=UpdatePasswordForm(), user=user
        )

    # If user is admin
    elif request.method == "POST":
        form = UpdatePasswordForm(request.form)
        if form.validate_on_submit():
            verified = User.verify_user(
                current_user.email, form.data.get("old_password")
            )
            if verified or current_user:
                updated = User.update_password(
                    email=current_user.email, password=form.data.get("new_password")
                )
                if updated:
                    Notifications.info_account_updated(**form.data)
                    login_user(current_user)
                    return redirect(url_for("account"))

        Notifications.info_try_again()
        return redirect(url_for("update_password"))


@app.route("/account/delete/<user_email>", methods=["GET", "POST"])
@login_required
def delete_account(user_email):
    if current_user.email == user_email:
        deleted = User.delete(email=user_email)
        if deleted:
            Notifications.success(message="Account was deleted successfully")
            return redirect(url_for("home"))


@app.route("/account", methods=["GET"])
@login_required
def account():
    return render_template(
        "pages/account.html", user=current_user, form=SignupForm(request.form)
    )


@login_required
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


# ADMIN ROUTES
# ----------------------------------------------------------------------------#
@app.route("/admin/users", methods=["GET"])
@login_required
def admin_users():
    if current_user.is_admin:
        users = User.query.all()
        return render_template(
            "pages/admin/accounts.html", users=users, form=SignupForm(request.form)
        )
    return render_template("errors/401.html"), 401


@app.route("/admin", methods=["GET"])
@login_required
def admin_stats():
    if current_user.is_admin:
        stats = dict()

        users = User.query.all()
        stats["users"] = len(users)

        books = Books.query.all()
        stats["books"] = len(books)

        return render_template(
            "pages/admin/accounts.html", stats=stats, form=EditAccountForm(request.form)
        )
    return render_template("errors/401.html"), 401


@app.route("/admin/account/edit/<user_email>", methods=["GET", "POST"])
@login_required
def edit_account(user_email):
    if request.method == "POST":
        form = EditAccountForm(request.form)
        if current_user.is_admin:
            updated = User.update(user_email, **form.data)
            if updated:
                Notifications.info_account_updated(**form.data)
                login_user(current_user)
                return redirect(url_for("admin_stats"))

        Notifications.info_try_again()
        return redirect(url_for("admin"))

    elif request.method == "GET":
        user = User.query.filter_by(email=user_email).first()
        return render_template(
            "pages/admin/accounts.html", form=EditAccountForm(), user=user
        )


@app.route("/admin/accounts/add", methods=["GET", "POST"])
@login_required
def add_account():
    if current_user.is_admin:
        if request.method == "GET":
            return render_template(
                "pages/admin/accounts.html", form=SignupForm(request.form)
            )

        elif request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            is_admin = request.form["is_admin"]

            # assume no user is created
            new_user = None
            if form.validate_on_submit():
                if email.split("@")[1].split(".")[0] == "cliqz":
                    # register user to db
                    new_user = User.register(name, email, user_type, password)
                if new_user is not None:
                    Notifications.info_account_created(name, password, email)
                    return redirect(url_for("accounts"))
                Notifications.info_try_again()
                return redirect(url_for("add_account"))

    return render_template("errors/401.html"), 401


# BOOKS ROUTES
# ----------------------------------------------------------------------------#
@app.route("/book/<book_id>", methods=["GET"])
def book(book_id):
    book = Books.get_book(id=book_id)
    if not book:
        return render_template("errors/404.html")
    reading_state = (None, None)

    # If user is authenticated, retrieve from DB the reading
    # state of the book for that user.
    if not current_user.is_anonymous:
        idx = UserBooks.get_reading_state(
            user_id=current_user.user_id,
            book_id=book_id
        )
        if idx is not None:
            reading_state = (idx, UserBooks.reading_state_repr.get(idx))

    # Get similar books
    sim_book_ids = SimilarBooks.get_sim_ids(book.get("goodreads_book_id"))
    similar_books = Books.get_list_from_goodreads_ids(ids=sim_book_ids)

    return render_template(
        "pages/book.html",
        book=book,
        form=LoginForm(request.form),
        reading_state=reading_state,
        similar_books=similar_books,
    )


# SERVICE HEALTH and ERROR HANDLERS
# ----------------------------------------------------------------------------#
@app.route("/health")
def health():
    return jsonify(status="OK")


@app.errorhandler(500)
def internal_error(error):
    # db_session.rollback()
    return render_template("errors/500.html"), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for("home"))


# Launch.
# ----------------------------------------------------------------------------#
if __name__ == "__main__":
    app.run(host="0.0.0.0")
