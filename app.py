from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from wtforms.validators import DataRequired,  EqualTo
from flask_wtf import FlaskForm
from flask_wtf import Form
from sqlalchemy.orm import sessionmaker
from wtforms import PasswordField, StringField, SubmitField, ValidationError

from flask import Flask, request, flash, url_for, redirect, render_template, session

engine = create_engine('sqlite:///:memory:', echo=True)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.sqlite3'
app.config['SECRET_KEY'] = "secret key"

Session = sessionmaker(bind=engine)

db = SQLAlchemy(app)



class Employees(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    designation = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    address = db.Column(db.String(100))
    pNumber = db.Column(db.String(50))
    manager = db.Column(db.String(200))
    password = db.Column(db.String(200))
    age = db.Column(db.String(10))

    def __init__(self, name, designation, salary, address, pNumber, manager, password, age):
        self.name = name
        self.designation = designation
        self.salary = salary
        self.address = address
        self.pNumber = pNumber
        self.manager = manager
        self.password = password
        self.age = age


class RegistrationForm(Form):

    name = StringField('name', validators=[DataRequired()])
    designation = StringField('designation', validators=[DataRequired()])
    salary = StringField('salary', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    pNumber=StringField('pNumber',validators=[DataRequired()])
    manager=StringField('manager',validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    age=StringField('age',validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if Employees.query.filter_by(name=field.data).first():
            raise ValidationError('Username is already in use.')

class LoginForm(FlaskForm):

    name = StringField('name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class DeleteForm(FlaskForm):

    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Delete')

class UpdateForm(Form):

    name = StringField('name', validators=[DataRequired()])
    designation = StringField('designation', validators=[DataRequired()])
    salary = StringField('salary', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    pNumber=StringField('pNumber',validators=[DataRequired()])
    manager=StringField('manager',validators=[DataRequired()])
    password=StringField('password',validators=[DataRequired()])
    age=StringField('age',validators=[DataRequired()])
    submit = SubmitField('Register')


class FeedbackForm(Form):

    name = StringField('name', validators=[DataRequired()])
    designation = StringField('designation', validators=[DataRequired()])
    salary = StringField('salary', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    pNumber=StringField('pNumber',validators=[DataRequired()])
    manager=StringField('manager',validators=[DataRequired()])
    password=StringField('password',validators=[DataRequired()])
    age=StringField('age',validators=[DataRequired()])
    submit = SubmitField('Register')



@app.route('/', methods=['GET', 'POST'])
def open_page():
    return render_template('/open.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        employee = Employees(name=form.name.data,
                            designation=form.designation.data,
                            salary=form.salary.data,
                            address=form.address.data,
                            pNumber=form.pNumber.data,
                            manager=form.manager.data,
                            password=form.password.data,
                            age=form.age.data)


        db.session.add(employee)
        db.session.commit()

        flash('You have successfully registered! You may now login.')
        return redirect(url_for('home_page'))
    return render_template('/register.html',form = form)

@app.route('/addEmp', methods=['GET','POST'])
def add_page():
    form = RegistrationForm()
    if form.validate_on_submit():
        employee = Employees(name=form.name.data,
                            designation=form.designation.data,
                            salary=form.salary.data,
                            address=form.address.data,
                            pNumber=form.pNumber.data,
                            manager=form.manager.data,
                            password=form.password.data,
                            age=form.age.data)


        db.session.add(employee)
        db.session.commit()

        flash('You have successfully registered! You may now login.')
        return redirect(url_for('list_employees'))
    return render_template('/add.html',form = form)
session1 = Session()
@app.route('/login', methods=['GET', 'POST'])
def home_page():

    form = LoginForm()
    if form.validate_on_submit():
            employee = Employees.query.filter_by(name=form.name.data).first()
            password=Employees.query.filter_by(password=form.password.data).first()
            print(employee)
            if employee is not None and password:
                if employee.name=="admin":
                    session['name'] = 'admin'
                    session1.add(employee)
                    return render_template('/superuser_logged_in_page.html')
                elif(Employees.query.filter_by(name=form.name.data).first()=="manager"):
                    session['name'] = employee.name
                    session1.add(employee)
                    return render_template('/manager_logged_in_page.html')
                else:
                    session['name'] = employee.name
                    current_db_sessions = session1.object_session(employee)
                    current_db_sessions.add(employee)
                    #session1.add(employee)
                    return render_template('/employee_logged_in_page.html',name=employee.name)
            else:
                print("invalid")


    return render_template('/home.html',form=form)

@app.route('/displayEmp')
def displayEmp():
        name1=(request.args.get('employee')[11:-1])
        employee = Employees.query.filter_by(name=name1).first()
        return render_template('/display.html',employee=employee)


@app.route('/logout')
def logout():
        return render_template('/open.html')

@app.route('/list')
def list_employees():
    return render_template('/list_employees.html', Employees=Employees.query.all())


@app.route('/del',methods=['GET', 'POST'])
def del_employees():
    form = DeleteForm()
    if request.method == 'POST':
        name = form.name.data
        employee = Employees.query.get_or_404(name)
        db.session.delete(employee)
        db.session.commit()
        flash('You have successfully deleted the department.')
        return redirect(url_for('list_employees'))

    return render_template('/delete.html', form=form)


@app.route('/give_feedback',methods=['GET', 'POST'])
def give_feedback():
    form = FeedbackForm()
    if request.method == 'POST':
        name = form.name.data
        employee = Employees.query.get_or_404(name)
        db.session.delete(employee)
        db.session.commit()
        flash('You have successfully deleted the department.')
        return redirect(url_for('list_employees'))

    return render_template('/delete.html', form=form)


@app.route('/update_profile_details', methods=['GET', 'POST'])
def update_profile_details():
    form = UpdateForm()
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
    form = UpdateForm()
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
        print('You have successfully updated! You may now login.')
        return redirect(url_for('home_page'))

    return render_template('/update_profile.html',form = form)

@app.route('/error')
def error():
    return render_template('/update_profile.html')

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html', title='Forbidden'), 403\

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html', title='Page Not Found'), 404

@app.errorhandler(500)
def internal_server_error(error):
        return render_template('errors/500.html', title='Server Error'), 500


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)


