from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import ValidationError
from wtforms.validators import InputRequired, Length, Regexp, EqualTo
from flask_pagedown.fields import PageDownField

from dailypush import db, constants
from dailypush.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(message="Username is required."),
            Length(
                min=constants.USERNAME_MIN_LENGTH,
                max=constants.USERNAME_MAX_LENGTH,
                message="Username is invalid.",
            ),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_-]+$",
                flags=0,  # https://docs.python.org/3/library/re.html#flags
                message="Usernames must have only letters, numbers, dashes"
                " or underscores.",
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Password is required."),
            Length(
                constants.PASSWORD_MIN_LENGTH,
                constants.PASSWORD_MAX_LENGTH,
                "Password is invalid.",
            ),
            Regexp(
                "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#$@!%&*?])[A-Za-z\d#$@!%&*?]*$",
                0,
                "Password is invalid.",
            ),
        ],
    )
    confirmation = PasswordField(
        "Confirm password",
        validators=[
            InputRequired(),
            EqualTo("password", "Passwords must match."),
        ],
    )

    def validate_username(self, field):
        if db.session.execute(db.select(User).filter_by(username=field.data)).scalar():
            raise ValidationError(f"Username '{field.data}' is already registered.")


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(message="Username is required.")]
    )
    password = PasswordField(
        "Password", validators=[InputRequired(message="Password is required.")]
    )


class CreateTopicForm(FlaskForm):
    title = StringField(
        "Topic name",
        validators=[InputRequired(), Length(max=100)],
    )


class PostForm(FlaskForm):
    title = StringField("Post title", validators=[Length(max=100)])
    body = PageDownField(
        "Post text", validators=[InputRequired("Post text is required.")]
    )
