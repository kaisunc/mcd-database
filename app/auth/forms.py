from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from ..models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    #first_name = StringField('First Name', validators=[DataRequired()])
    #last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')

    # check the db if name is unique
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username exists!')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],  render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    