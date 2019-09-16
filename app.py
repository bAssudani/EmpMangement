import os
import sqlite3
from bson import ObjectId
from pymongo import MongoClient
from redis import Redis
import pymongo
import models
import flask_redis
import flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired,  EqualTo
from flask_wtf import FlaskForm
from flask_wtf import Form
from datetime import timedelta
from flask import session, app
from flask_login import LoginManager, login_user, logout_user
from wtforms import PasswordField, StringField, SubmitField, ValidationError, IntegerField, validators, RadioField
from flask import Flask, request, flash, url_for, redirect, render_template, session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.sqlite3'
app.config['SECRET_KEY'] = "secret key"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['REDIS_HOST'] = 'localhost'
app.config['REDIS_PORT'] = 6379
app.config['REDIS_DB'] = 0
client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client.Assessment    #Select the database
forms = db.Form #Select the collection name
redis = Redis(app)

db = SQLAlchemy(app)


class Employees(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    designation = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    address = db.Column(db.String(100))
    pNumber = db.Column(db.Integer)
    manager = db.Column(db.String(200))
    password = db.Column(db.String(200))
    age = db.Column(db.Integer)
    isManager=db.Column(db.Boolean)

    def __init__(self, name, designation, salary, address, pNumber, manager, password, age,isManager):
        self.name = name
        self.designation = designation
        self.salary = salary
        self.address = address
        self.pNumber = pNumber
        self.manager = manager
        self.password = password
        self.age = age
        self.isManager=isManager

db.create_all()

@app.route('/', methods=['GET', 'POST'])
def open_page():
    return render_template('/open.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = models.RegistrationForm()
    if form.validate_on_submit():
        employee = Employees(name=form.name.data,
                            designation=form.designation.data,
                            salary=form.salary.data,
                            address=form.address.data,
                            pNumber=form.pNumber.data,
                            manager=form.manager.data,
                            password=form.password.data,
                            age=form.age.data,isManager=False)
        f = open("manager.txt", "r")
        f1 = f.readlines()
        for x in f1:

            if (str(x)[:-1] == str(form.name.data)):
                employee.isManager = True

        f = open("manager.txt", "a")
        f.write(employee.manager + "\n")
        db.session.add(employee)
        db.session.commit()
        flash('You have successfully registered! You may now login.')
        return redirect(url_for('home_page'))
    return render_template('/register.html',form = form)



@app.route('/login', methods=['GET', 'POST'])
def home_page():
    form = models.LoginForm()
    if form.validate_on_submit():

            employee = Employees.query.filter_by(name=form.name.data).first()
            password=Employees.query.filter_by(password=form.password.data).first()
            if employee is not None and password:
                if employee.name=="admin":
                    session['name'] = 'admin'
                    return render_template('/superuser_logged_in_page.html')
                elif(employee.isManager):
                    session['name'] = employee.name
                    return render_template('/manager_logged_in_page.html',name=employee.name)
                else:
                    session['name'] = employee.name
                    return render_template('/employee_logged_in_page.html',name=employee.name)
            else:
                print("invalid")


    return render_template('/home.html',form=form)


@app.route('/addEmp', methods=['GET','POST'])
def add_page():
    form = models.RegistrationForm()
    if form.validate_on_submit():
        isManage=False
        employee = Employees(name=form.name.data,
                            designation=form.designation.data,
                            salary=form.salary.data,
                            address=form.address.data,
                            pNumber=form.pNumber.data,
                            manager=form.manager.data,
                            password=form.password.data,
                            age=form.age.data,isManager=False)

        f = open("manager.txt", "r")
        f1 = f.readlines()
        for x in f1:
            if (x == form.name.data):
                employee.isManager = True
                employee = Employees(name=form.name.data,
                                     designation=form.designation.data,
                                     salary=form.salary.data,
                                     address=form.address.data,
                                     pNumber=form.pNumber.data,
                                     manager=form.manager.data,
                                     password=form.password.data,
                                     age=form.age.data, isManager=True)

        f = open("manager.txt", "a")
        f.write(employee.manager + "\n")
        db.session.add(employee)
        db.session.commit()
        flash('You have successfully registered! You may now login.')
        return redirect(url_for('list_employees'))
    return render_template('/add.html',form = form)


@app.route('/displayEmp')
def displayEmp():
        name1=(request.args.get('employee')[11:-1])
        employee = Employees.query.filter_by(name=name1).first()
        return render_template('/display.html',employee=employee)



@app.route('/search', methods=['GET', 'POST'])
def search_emp():
        searchForm = models.SearchForm()
        employees = Employees.query
        if searchForm.validate_on_submit() :
            conn = sqlite3.connect('employees.sqlite3')
            c = conn.cursor()
            c.execute("select * from Employees where name like ?", ('%' + searchForm.name.data + '%',))
            rows = c.fetchall()
            return render_template('list_employees_search.html', rows=rows)

        return render_template('/search.html',form=searchForm)

@app.route('/logout')
def logout():
        return render_template('/open.html')

@app.route('/list')
def list_employees():
    logged_in=session['name']
    employee = Employees.query.filter_by(name=logged_in).first()
    if(employee.isManager):
        rows=Employees.query.filter_by(manager=logged_in).all()
        return render_template('/list_employees.html', rows=rows)
    else:
        return render_template('/list_employees.html', rows=Employees.query.all())

@app.route('/back')
def back_emp():
    logged_in=session['name']
    employee = Employees.query.filter_by(name=logged_in).first()
    if logged_in=="admin":
                    return render_template('/superuser_logged_in_page.html')
    elif(employee.isManager):
                    return render_template('/manager_logged_in_page.html',name=employee.name)
    else:
                   return render_template('/employee_logged_in_page.html',name=employee.name)


@app.route('/del',methods=['GET', 'POST'])
def del_employees():
    form = models.DeleteForm()
    if request.method == 'POST':
        name = form.name.data
        employee = Employees.query.get_or_404(name)
        db.session.delete(employee)
        db.session.commit()
        flash('You have successfully deleted the department.')
        return redirect(url_for('list_employees'))

    return render_template('/delete.html', form=form)

'''
@app.route('/feedback',methods=['GET', 'POST'])
def feedback_emp():
    form = FeedbackForm()
    if request.method == 'POST':
        name = form.name.data
        logged_in = session['name']
        employee = Employees.query.filter_by(name=logged_in).first()
        rows = Employees.query.filter_by(manager=logged_in).all()
        for emp in rows:
            if(emp.name==name):
                f = open("feedback.txt", "a")
                f.write( '\n'+form.name.data+"\n"+form.feedback.data)
                flash("feedback submitted")
                return redirect(url_for('list_employees'))
            else:
                print('no one to give feedback')
    return render_template('/feedbac.html', form=form)
'''
@app.route('/feedback',methods=['post','get'])
def feedback_emp():
    form = models.SimpleForm()
    if form.validate_on_submit():
        name = form.name.data
        logged_in = session['name']
        employee = Employees.query.filter_by(name=logged_in).first()
        rows = Employees.query.filter_by(manager=logged_in).all()
        for emp in rows:
            if (emp.name == name):

                mydict = {"name": name, "job-knowledge": form.example.data}
                forms.insert_one(mydict)

                flash("feedback submitted")
                return redirect(url_for('list_employees'))
            else:
                flash('no one to give feedback')

    return render_template('example.html',form=form)

@app.route('/feedbackShow',methods=['GET', 'POST'])
def feedback_view():
        logged_in = session.get('name')
        f = open("feedback.txt", "r")
        f1 = f.readlines()
        if request.method == 'GET':
            todos_1=forms.find( { "name": logged_in } )
            for i in todos_1:
                feedback=(i['job-knowledge'])

        return render_template('/Showfeedback.html',feedback=feedback)

@app.route('/update_profile_details', methods=['GET', 'POST'])
def update_profile_details():
    form = models.UpdateForm()
    if request.method == 'POST':
       name=form.name.data
       employee = Employees.query.get_or_404(name)
       employee.designation=form.designation.data
       employee.salary=form.salary.data
       employee.address=form.address.data
       employee.pNumber=form.pNumber.data
       employee.manager=form.manager.data
       employee.password=form.password.data
       employee.age=form.age.data
       db.session.commit()
       print('You have successfully registered! You may now login.')
       return redirect(url_for('list_employees'))

    return render_template('/updateForm.html',form = form)


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    form = models.UpdateForm()
    if request.method == 'POST' and form.name.data==session['name']:
        name = form.name.data
        employee = Employees.query.get_or_404(name)
        employee.designation=form.designation.data
        employee.salary=form.salary.data
        employee.address=form.address.data
        employee.pNumber=form.pNumber.data
        employee.manager=form.manager.data
        employee.password=form.password.data
        employee.age=form.age.data
        db.session.commit()
        flash('You have successfully updated! You may now login.')
        return redirect(url_for('home_page'))

    return render_template('/update_profile.html',form = form)

if __name__ == '__main__':
    app.run(debug=True)


