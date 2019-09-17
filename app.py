import sqlite3
from pymongo import MongoClient
from redis import Redis
import models
import logging
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask import Flask, request, flash, url_for, redirect, render_template, session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.sqlite3'
app.config['SECRET_KEY'] = "secret key"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['REDIS_HOST'] = 'localhost'
app.config['REDIS_PORT'] = 6379
app.config['REDIS_DB'] = 0

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.Assessment
forms = db.Form
redis = Redis(app)

log = "LoggerFile.log"
logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

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
        try:
            db.session.add(employee)
            db.session.commit()
            flash('You have successfully registered! You may now login.')
            logging.info(' registered successfully')
            return redirect(url_for('home_page'))
        except Exception as e:
            logging.info(form.name.data, 'failed to register successfully')
            return render_template("errors/500.html", error = str(e))

    return render_template('/register.html',form = form)



@app.route('/login', methods=['GET', 'POST'])
def home_page():
    form = models.LoginForm()
    try:
        if form.validate_on_submit():

            employee = Employees.query.filter_by(name=form.name.data).first()
            password=Employees.query.filter_by(password=form.password.data).first()
            if employee is not None and password:
                if employee.name=="admin":
                    session['name'] = 'admin'
                    logging.info("logged in as admin")
                    return render_template('/superuser_logged_in_page.html')
                elif(employee.isManager):
                    session['name'] = employee.name
                    logging.info("logged in as Manager ")
                    return render_template('/manager_logged_in_page.html',name=employee.name)
                else:
                    session['name'] = employee.name
                    logging.info("logged in as employee ")
                    return render_template('/employee_logged_in_page.html',name=employee.name)
            else:
                logging.error("failed to log in")
                flash("invalid username or password")
    except Exception as e:
        logging.error("failed to log in")
        return render_template("errors/500.html", error = str(e))
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
        try:
            db.session.add(employee)
            db.session.commit()
            flash('You have successfully added an employee! ')
            logging.info("employee added successfully")
            return redirect(url_for('list_employees'))
        except Exception as e:
            logging.error("unable to add employee")
            return render_template("errors/500.html", error = str(e))
    return render_template('/add.html',form = form)


@app.route('/displayEmp')
def displayEmp():
        name1=(request.args.get('employee')[11:-1])
        employee = Employees.query.filter_by(name=name1).first()
        logging.info("employees list displayed")
        return render_template('/display.html',employee=employee)



@app.route('/search', methods=['GET', 'POST'])
def search_emp():
        searchForm = models.SearchForm()
        employees = Employees.query
        if searchForm.validate_on_submit() :
          try:
            conn = sqlite3.connect('employees.sqlite3')
            c = conn.cursor()
            c.execute("select * from Employees where name like ?", ('%' + searchForm.name.data + '%',))
            rows = c.fetchall()
            logging.info("search results shown")
            return render_template('list_employees_search.html', rows=rows)
          except Exception as e:
              logging.error("search results couldnt be shown")
              return render_template("500.html", error=str(e))

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
        logging.info("employees list shown")
        return render_template('/list_employees.html', rows=rows)
    else:
        logging.info("employees list shown")
        return render_template('/list_employees.html', rows=Employees.query.all())

@app.route('/back')
def back_emp():
    try:
        logged_in=session['name']
        employee = Employees.query.filter_by(name=logged_in).first()
        if logged_in=="admin":
                    return render_template('/superuser_logged_in_page.html')
        elif(employee.isManager):
                    return render_template('/manager_logged_in_page.html',name=employee.name)
        else:
                   return render_template('/employee_logged_in_page.html',name=employee.name)
    except Exception as e:
        return render_template('/open.html')


@app.route('/del',methods=['GET', 'POST'])
def del_employees():
    form = models.DeleteForm()
    if request.method == 'POST':
        name = form.name.data
        employee = Employees.query.get(name)

        try:
            if employee :

                db.session.delete(employee)
                db.session.commit()
                flash('You have successfully deleted the employee.')
                logging.info("employee deleted successfully")
                return redirect(url_for('list_employees'))

            else:
                logging.error("no employee to delete or couldnt delete")
                flash("employee not present to delete")

        except Exception as e:
            logging.error("couldnt delete")
            return  render_template("500.html", error = str(e))

    return render_template('/delete.html', form=form)


@app.route('/feedback',methods=['post','get'])
def feedback_emp():
    form = models.SimpleForm()
    try:
        if form.validate_on_submit():
            name = form.name.data
            logged_in = session['name']
            rows = Employees.query.filter_by(manager=logged_in).all()
            for emp in rows:
                if (emp.name == name):
                    mydict = {"name": name, "job-knowledge": form.example.data}
                    forms.insert_one(mydict)
                    flash("feedback submitted")
                    logging.info("feedback submitted ")
                    return redirect(url_for('list_employees'))
            else:
                logging.error("cannot give feedback")
                flash('no one to give feedback')
    except Exception as e:
        logging.error("couldnt submit feedback")
        return(str(e))
    return render_template('example.html',form=form)

@app.route('/feedbackShow', methods=['GET', 'POST'])
def feedback_view():
        logged_in = session.get('name')
        if request.method=='GET':
            todos_1=forms.find( { "name": logged_in } )
            feedback="no assessment to show"
            for i in todos_1:
                feedback=(i['job-knowledge'])
        return render_template('/Showfeedback.html',feedback=feedback)


@app.route('/update_profile_details', methods=['GET', 'POST'])
def update_profile_details():
    form = models.UpdateForm()
    if request.method == 'POST':
       name=form.name.data
       employee = Employees.query.get(name)
       if employee:
           employee.designation=form.designation.data
           employee.salary=form.salary.data
           employee.address=form.address.data
           employee.pNumber=form.pNumber.data
           employee.manager=form.manager.data
           employee.password=form.password.data
           employee.age=form.age.data
           try:
               db.session.commit()
               flash('You have successfully updated!')
               logging.info("profile updated successfully by ",name)
               return redirect(url_for('list_employees'))
           except Exception as e:
                logging.error("profile cannot be updated")
                flash("cannot update! view details again")
       else:
           logging.error("profile cannot be updated")
           flash("cannot update view name again")
    return render_template('/updateForm.html',form = form)


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    form = models.UpdateForm()
    if request.method == 'POST' :
      if form.name.data==session['name']:
        name = form.name.data
        employee = Employees.query.get(name)
        if employee:
            employee.designation=form.designation.data
            employee.salary=form.salary.data
            employee.address=form.address.data
            employee.pNumber=form.pNumber.data
            employee.manager=form.manager.data
            employee.password=form.password.data
            employee.age=form.age.data
            try:
                db.session.commit()
                flash('You have successfully updated! You may now login.')
                logging.info("succesfully updated profile by")
                return redirect(url_for('home_page'))
            except Exception as e:
                logging.error("cannot update profile")
                flash("cannot update! view details again")
      else:
            logging.error("cannot update view name gain")
            flash("cannot update view name again")

    return render_template('/update_profile.html',form = form)

@app.route('/givefeedback',methods=['GET',"POST"])
def give_feedback():
    form=models.Feedback()
    if request.method == "POST":
        manager=form.name.data
        logged_in=session['name']
        employee = Employees.query.get(logged_in)

        if(employee.manager==manager):
            try:
                f = open("feedback.txt", "a")
                f.write('\n' + form.name.data + "\n" + form.message.data)
                flash("feedback submitted successfully")
                logging.info("feedback submitted successfully for ",form.name.data)
            except Exception as e:
                logging.error("cannot submit feedback")
                flash("cannot submit feedback please try again")
        else:
            logging.error("cannot submit feedback")
            flash("u can give feedback for ur manager only")
    return render_template('/submitFeedback.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)


