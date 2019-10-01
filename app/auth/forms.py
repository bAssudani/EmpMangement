from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from ..models import Employee



class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('name', validators=[DataRequired(message="cannot be null and is a string")])
    designation = StringField('designation', validators=[DataRequired(message="cannot be null and is a string")])
    salary = IntegerField('salary', validators=[DataRequired(message="cannot be null and is an integer")])
    address = StringField('address', validators=[DataRequired(message="cannot be null and is a string")])
    pNumber = IntegerField('pNumber', validators=[DataRequired(message="cannot be null and is an integer")])
    manager = StringField('manager', validators=[DataRequired(message="cannot be null and is a string")])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password')
    ])
    confirm_password = PasswordField('Confirm Password')
    age = IntegerField('age', validators=[DataRequired(message="cannot be null and is an integer")])
    submit = SubmitField('Register')

    def validate_name(self, field):
        if Employee.query.filter_by(name=field.data).first():
            raise ValidationError('Username is already in use.')

    def validate_email(self, field):
        if Employee.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(message="cannot be null and is a string ")])
    password = PasswordField('Password', validators=[DataRequired(message="is incorrect ")])
    submit = SubmitField('Login')


