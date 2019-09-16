# from all_packages import *
# from app import Employees
# import os
# import sqlite3
import flask
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired,  EqualTo
from flask_wtf import FlaskForm
from flask_wtf import Form
# from datetime import timedelta
# from flask import session, app
# from flask_login import LoginManager, login_user, logout_user
from wtforms import PasswordField, StringField, SubmitField, ValidationError, IntegerField, validators, RadioField
from flask import Flask, request, flash, url_for, redirect, render_template, session
from app import Employees


class RegistrationForm(Form):
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
        if Employees.query.filter_by(name=field.data).first():
            raise ValidationError('Username is already in use.')


class LoginForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(message="cannot be null and is a string ")])
    password = PasswordField('Password', validators=[DataRequired(message="is incorrect ")])
    submit = SubmitField('Login')


class DeleteForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(message="cannot be null and is a string ")])
    submit = SubmitField('Delete')


class UpdateForm(Form):
    name = StringField('name', validators=[DataRequired(message="cannot be null and is a string ")])
    designation = StringField('designation', validators=[DataRequired(message="cannot be null and is a string")])
    salary = IntegerField('salary', validators=[DataRequired(message="cannot be null and is an integer")])
    address = StringField('address', validators=[DataRequired(message="cannot be null and is a string")])
    pNumber = IntegerField('pNumber', validators=[DataRequired(message="cannot be null and is an integer")])
    manager = StringField('manager', validators=[DataRequired(message="cannot be null and is an integer")])
    password = PasswordField('password', validators=[DataRequired(message="cannot be null and is a string")])
    age = IntegerField('age', validators=[DataRequired(message="cannot be null and is an integer")])
    submit = SubmitField('Update')

    def validate_name(self, field):
        if session['name'] != field.data:
            raise ValidationError('Username is not correct.')


class FeedbackForm(Form):
    name = StringField('name', validators=[DataRequired()])
    feedback = StringField('feedback', validators=[DataRequired()])
    submit = SubmitField('Give Feedback')


class SimpleForm(Form):
    name = StringField('name', validators=[DataRequired()])
    example = RadioField('Label', choices=[('Excellent', 'Excellent'), ('Very Good', 'Very Good'), ('Good', 'Good'),
                                           ('Satisfactory', 'Satisfactory'), ('Need improvement', 'Need improvement')])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Search')
