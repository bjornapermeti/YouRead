from flask import flash, Markup


class Notifications:
    @classmethod
    def success(cls, message):
        return flash(message=Markup(message), category="success")

    @classmethod
    def info_bad_login(cls):
        return flash(
            message=Markup(
                "Bad <code>email</code> and/or <code>password</code>. Try again!"
            ),
            category="error",
        )

    @classmethod
    def email_exists(cls, email):
        return flash(
            message=Markup(
                f"Account with e-mail: <strong>{email}</strong> already exists."
            ),
            category="error",
        )

    @classmethod
    def password_too_short(cls):
        return flash(
            message=Markup(
                "Password is too short. A good password should be at least 10 characters long"
            ),
            category="error",
        )

    @classmethod
    def info_try_again(cls):
        return flash(message="Please try again!", category="error")

    @classmethod
    def info_account_created(cls, name, password, email):
        return flash(
            message=Markup(f"Hello <strong>{name}</strong>! Welcome to YouRead"),
            category="success",
        )

    @classmethod
    def info_account_updated(cls, **kwargs):
        return flash(
            message=Markup(
                "Update: "
                + " ,".join(
                    [
                        "<code>" + k + "</code>: " + "<code>" + v + "</code>"
                        for (k, v) in kwargs.items()
                        if v
                    ]
                )
            ),
            category="success",
        )
