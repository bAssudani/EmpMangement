from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager



class Employee(UserMixin, db.Model):

    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(60))
    designation = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    address = db.Column(db.String(100))
    pNumber = db.Column(db.Integer)
    manager = db.Column(db.String(200))
    password_hash = db.Column(db.String(128))
    age = db.Column(db.Integer)
    isManager=db.Column(db.Boolean)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_admin = db.Column(db.Boolean, default=False)
    assessment = db.Column(db.String(200))
    feedback = db.Column(db.String(200))
    leave_id = db.Column(db.Integer, db.ForeignKey('leaves.id'))
    photo=db.Column(db.LargeBinary)


    @property
    def password(self):

        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):

        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):

        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<Employee: {}>'.format(self.name)



@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))


class Department(db.Model):


    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    employees = db.relationship('Employee', backref='department',
                                lazy='dynamic')

    def __repr__(self):
        return '<Department: {}>'.format(self.name)


class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    employee = db.relationship('Employee', backref='role',
                                lazy='dynamic')

    def __repr__(self):
        return '<Role: {}>'.format(self.name)

    def __iter__(self):

        return {'name':self.name,'description':self.description}


class Leave(db.Model):

    __tablename__ = 'leaves'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    name = db.Column(db.String(60))
    date_from = db.Column(db.DateTime)
    date_to = db.Column(db.DateTime)
    days = db.Column(db.Integer)
    leave_reason = db.Column(db.String(200))
    leave_status = db.Column(db.String(200))
    employee1 = db.relationship('Employee', backref='leave',
                                lazy='dynamic')

    def __repr__(self):
        return '<Leave: {}>'.format(self.name)
