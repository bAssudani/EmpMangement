import json
import re

from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from sqlalchemy import or_
from wtforms import StringField, SubmitField, IntegerField, PasswordField, BooleanField, RadioField, validators, \
    FileField, widgets
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, InputRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.widgets import PasswordInput

from ..models import Department, Role, Employee
from wtforms.fields.html5 import DateField

class DepartmentForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RoleForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EmployeeAssignForm(FlaskForm):

    department = QuerySelectField(query_factory=lambda: Department.query.all(),
                                  get_label="name")
    role = QuerySelectField(query_factory=lambda: Role.query.all(),
                            get_label="name")
    submit = SubmitField('Submit')

class EmployeeEditForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={'readonly': True})
    name = StringField('Name', validators=[DataRequired(message="cannot be null and is a string")])
    designation = StringField('Designation', validators=[DataRequired(message="cannot be null and is a string")])
    salary = IntegerField('Salary', validators=[DataRequired(message="cannot be null and is an integer")])
    address = StringField('Address', validators=[DataRequired(message="cannot be null and is a string")])
    pNumber = IntegerField('Phone Number', validators=[DataRequired(message="cannot be null and is an integer")])
    manager = QuerySelectField('Manager-Id',query_factory=lambda:Employee.query.filter(Employee.isManager==1).all(),
                                  get_label="id", validators=[DataRequired(message="cannot be null ")])
    age = IntegerField('Age', validators=[DataRequired(message="cannot be null and is an integer")])
    submit = SubmitField('Update')
    def validate_pNumber(self, field):
        if len(str(field.data))!= 10 :
            raise ValidationError('Phone Number should be of 10 digits')



class EmployeeAddForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(message="cannot be null and is a string")])
    designation = StringField('Designation', validators=[DataRequired(message="cannot be null and is a string")])
    salary = IntegerField('Salary', validators=[DataRequired(message="cannot be null and is an integer")])
    address = StringField('Address', validators=[DataRequired(message="cannot be null and is a string")])
    pNumber = IntegerField('Phone Number', validators=[DataRequired(message="cannot be null and is an integer")])
    manager = QuerySelectField('Manager-Id',query_factory=lambda: Employee.query.filter(Employee.isManager==1).all(),
                                  get_label="id")
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password')
    ])
    confirm_password = PasswordField('Confirm Password')
    isManager = BooleanField('Is Manager?')
    age = IntegerField('Age', validators=[DataRequired(message="cannot be null and is an integer")])
    photo = FileField('Picture',validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Add')

    def validate_email(self, field):
        if Employee.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_pNumber(self, field):
        if len(str(field.data))!= 10 :
            raise ValidationError('Phone Number should be of 10 digits')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError("Make sure your password is at lest 8 letters")
        elif re.search('[0-9]', field.data) is None:
            raise ValidationError("Make sure your password has a number in it")
        elif re.search('[A-Z]', field.data) is None:
            raise ValidationError("Make sure your password has a capital letter in it")


class AssessmentForm(FlaskForm):
    name = QuerySelectField('Employee' ,query_factory=lambda: Employee.query.filter_by(manager=current_user.name).all(),
                                  get_label="name")
    example = RadioField('Job Knowledge', validators=[InputRequired()] , choices=[('Excellent', 'Excellent'), ('Very Good', 'Very Good'), ('Good', 'Good'),
                                           ('Satisfactory', 'Satisfactory'), ('Need improvement', 'Need improvement')])
    submit = SubmitField('Submit')

    def pre_validate(self, form):
        for v, _ in self.choices:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))



class FeedbackForm(FlaskForm):
    name=QuerySelectField('Manager',query_factory=lambda: Employee.query.filter_by(name=current_user.manager).all(),
                                  get_label="name")
    feedback = StringField('Feedback', validators=[DataRequired()])
    submit = SubmitField('Give Feedback')

class UpdateForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired(message="cannot be null and is an integer")],render_kw={'readonly': True})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={'readonly': True})
    name = StringField('Name', validators=[DataRequired(message="cannot be null and is a string")],render_kw={'readonly': True})
    designation = StringField('Designation', validators=[DataRequired(message="cannot be null and is a string")],render_kw={'readonly': True})
    address = StringField('Address', validators=[DataRequired(message="cannot be null and is a string")],render_kw={'readonly': True})
    manager = StringField('Manager', validators=[DataRequired(message="cannot be null and is a string")],render_kw={'readonly': True})
    age = IntegerField('Age', validators=[DataRequired(message="cannot be null and is an integer")],render_kw={'readonly': True})

class UpdateFormAdmin(FlaskForm):
    id = IntegerField('id', validators=[DataRequired(message="cannot be null and is an integer")],render_kw={'readonly': True})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={'readonly': True})
    name = StringField('name', validators=[DataRequired(message="cannot be null and is a string")])
    designation = StringField('designation', validators=[DataRequired(message="cannot be null and is a string")])
    address = StringField('address', validators=[DataRequired(message="cannot be null and is a string")])
    age = IntegerField('age', validators=[DataRequired(message="cannot be null and is an integer")])
    submit = SubmitField('Save')

class SearchForm(FlaskForm):
  search = StringField('search',default="")
  submit = SubmitField('Search')

class LeaveForm(FlaskForm):
    dt = DateField('Leave From')
    dt1 = DateField('Leave To')
    submit = SubmitField('Apply')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password')
    ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Change')

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError("Make sure your password is at lest 8 letters")
        elif re.search('[0-9]', field.data) is None:
            raise ValidationError("Make sure your password has a number in it")
        elif re.search('[A-Z]', field.data) is None:
            raise ValidationError("Make sure your password has a capital letter in it")