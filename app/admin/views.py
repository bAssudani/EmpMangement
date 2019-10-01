import json
import logging
import os
import pickle

import redis
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from elasticsearch import Elasticsearch
from flask import abort, flash, redirect, render_template, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from forms import DepartmentForm, RoleForm, EmployeeEditForm, EmployeeAddForm, AssessmentForm, FeedbackForm, UpdateForm, \
    SearchForm, LeaveForm, UpdateFormAdmin
from ..models import Department, Role, Leave
from . import admin
from .. import db
from forms import DepartmentForm, EmployeeAssignForm, RoleForm
from ..models import Department, Employee, Role


logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)



es = Elasticsearch()
redisClient = redis.Redis(host='localhost',port=6379,db=0)


def check_admin():
    if not current_user.is_admin:
        abort(403)

def check_manager():
    if not current_user.isManager:
        abort(403)


@admin.route('/departments', methods=['GET', 'POST'])
@login_required
def list_departments():
    check_admin()
    departments = Department.query.all()
    logger.info("departments list shown")
    return render_template('admin/departments/departments.html',
                           departments=departments, title="Departments")


@admin.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    check_admin()
    add_department = True
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data,
                                description=form.description.data)
        try:

            db.session.add(department)
            db.session.commit()
            logger.info('department added successfully')

            flash('You have successfully added a new department.')
        except:
            logger.error('department couldnt be added')
            flash('Error: department name already exists.')


        return redirect(url_for('admin.list_departments'))


    return render_template('admin/departments/department.html', action="Add",
                           add_department=add_department, form=form,
                           title="Add Department")


@admin.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):

    check_admin()

    add_department = False

    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data
        department.description = form.description.data
        try:
            db.session.commit()
            logger.info('department edited succesflly')
            flash('You have successfully edited the department.')
            return redirect(url_for('admin.list_departments'))
        except Exception as e:
            logger.error('department couldnt be edited')
            flash("cannot edit department try again")

    form.description.data = department.description
    form.name.data = department.name
    return render_template('admin/departments/department.html', action="Edit",
                           add_department=add_department, form=form,
                           department=department, title="Edit Department")


@admin.route('/departments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    check_admin()
    department = Department.query.get_or_404(id)
    try:
        db.session.delete(department)
        db.session.commit()
        logger.info('department deleted ')
        flash('You have successfully deleted the department.')
        return redirect(url_for('admin.list_departments'))
    except Exception as e:
        logger.error('cannot delete department')
        flash('cannot delete')
    return render_template(title="Delete Department")



@admin.route('/roles')
@login_required
def list_roles():
    check_admin()
    roles = Role.query.all()
    logger.info('roles list shown')
    return render_template('admin/roles/roles.html',
                           roles=roles, title='Roles')


@admin.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    check_admin()
    add_role = True
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data,
                    description=form.description.data)
        try:
            db.session.add(role)
            db.session.commit()
            logger.info('role added')
            flash('You have successfully added a new role.')
        except Exception as e:
            logger.error('role cannot be added')

            flash(e)


        return redirect(url_for('admin.list_roles'))


    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title='Add Role')


@admin.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    check_admin()
    add_role = False
    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        try:
            db.session.add(role)
            db.session.commit()
            logger.info('role edited ')
            flash('You have successfully edited the role.')
            return redirect(url_for('admin.list_roles'))
        except Exception as e:
            logger.error('role cannot be edited')
            flash("cannot edit")
    form.description.data = role.description
    form.name.data = role.name
    return render_template('admin/roles/role.html', add_role=add_role,
                           form=form, title="Edit Role")


@admin.route('/roles/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_role(id):
    check_admin()
    role = Role.query.get_or_404(id)
    try:
        db.session.delete(role)
        db.session.commit()
        logger.info('role deleted')
        flash('You have successfully deleted the role.')
        return redirect(url_for('admin.list_roles'))
    except Exception as e:
        logger.info('role cannot be deleted')
        flash("cannot delete")
    return render_template(title="Delete Role")

@admin.route('/employees')
@login_required
def list_employees():
    check_admin()
    logger.info('employees list shown from redis')
    employees=Employee.query.all()
    return render_template('admin/employees/employees.html',
                           employees=employees, title='Employees')


@admin.route('/sub')
@login_required
def view_sub():
    logged_in=current_user.name
    employees = Employee.query.filter_by(manager=logged_in).all()
    logger.info('subordinates list shown')
    return render_template('admin/employees/subordinates.html',
                           employees=employees, title='Employees')

@admin.route('/search', methods=['GET', 'POST'])
@login_required
def search_employees():
    form = SearchForm()
    employees = []
    while (redisClient.llen('c') != 0):
        (redisClient.lpop('c'))
    emp = Employee.query.all()
    for x in emp:
        redisClient.lpush('c', pickle.dumps(x))
    l = redisClient.lrange('c', 0, -1)
    for x in l:
        employees.append(pickle.loads(x))

    if request.method == "POST":
        try:
            pattern = form.search.data

            body_search={
                "query": {

                "regexp": {
                    "name": '.*'+pattern+'.*'
                }

            }
            }
            #print(es.get(index='contents1', doc_type='title', id=37))
            r = es.search(index='contents2', body=body_search)
            roles=[]
            for x in r['hits']['hits']:
                print(x['_source']['name'])
                roles.append(x['_source'])
            return render_template('admin/employees/search_results1.html',
                                   employees=roles, title='Employees',form=form)
        except Exception as e:
            print e
    return render_template('admin/employees/search.html', title='Employees', form=form,employees=employees)


@admin.route('/search_results')
@login_required
def search_results(record):
    logger.info('search results shown')
    return render_template('admin/employees/search_results.html',
                           employees=record, title='Employees')

@admin.route('/employees1')
@login_required
def list_employees1():
    employees=[]
    while (redisClient.llen('c') != 0):
        (redisClient.lpop('c'))
    emp=Employee.query.all()
    for x in emp:
        redisClient.lpush('c',pickle.dumps(x))
    l = redisClient.lrange('c', 0, -1)
    for x in l:
        employees.append(pickle.loads(x))
    logger.info('employees list shown from redis')
    return render_template('admin/employees/employees3.html', employees=employees, title='Employees')




@admin.route('/employees2')
@login_required
def list_employees2():
    l = redisClient.lrange('EmployeeList', 0, -1)
    for employee in l:
          redisClient.lpop(employee)
    empList=Employee.query.all()
    employee=[]
    for emp in empList:
        redisClient.lpush('EmployeeList',emp)
        employee.append(emp)

    return render_template('admin/employees/employees1.html', employees=employee, title='Employees')

@admin.route('/employees/assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_employee(id):
    check_admin()
    employee = Employee.query.get_or_404(id)
    if employee.is_admin:
        abort(403)
    form = EmployeeAssignForm(obj=employee)
    if form.validate_on_submit():
        employee.department = form.department.data
        employee.role = form.role.data
        try:
            db.session.add(employee)
            db.session.commit()
            logger.info('employee assigned succesfully')
            flash('You have successfully assigned a department and role.')
            return redirect(url_for('admin.list_employees'))
        except Exception as e:
            logger.error('employee cannot be assigned')
            flash("cannot assign")
    return render_template('admin/employees/employee.html',
                           employee=employee, form=form,
                           title='Assign Employee')

@admin.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    check_admin()
    employee = Employee.query.get_or_404(id)
    form = EmployeeEditForm(obj=employee)
    if form.validate_on_submit():
        employee.email = form.email.data
        employee.name = form.name.data
        employee.designation = form.designation.data
        employee.salary = form.salary.data
        employee.address = form.address.data
        employee.pNumber = form.pNumber.data
        employee.manager = str(form.manager.data)[11:-1]
        employee.age = form.age.data
        try:
            db.session.commit()

            body = {
                'id':employee.id,
                'name': employee.name,
                'designation': employee.designation,
                'manager': employee.manager,
                'age': employee.age

            }
            redisClient.hmset('e' + str(employee.id), body)
            es.index(index='contents2', doc_type='title', id=employee.id, body=body)
            logger.info('employee edited')
            flash('You have successfully edited an employee.')
            return redirect(url_for('admin.list_employees'))
        except Exception as e:
            flash('cannot edit')
    return render_template('admin/employees/edit.html',action="edit",
                           employee=employee, form=form,
                           title='Edit Employee')

'''    
    if redisClient.exists()
    if redisClient.exists('e'+str(current_user.id)):
        logger.info('employees profile shown from redis')
        return redirect(url_for('admin.view_profile_redis'))
    
    else:

        form = UpdateForm(obj=employee)
        if form.validate_on_submit():
            employee.email = form.email.data
            employee.name = form.name.data
            employee.designation = form.designation.data
            employee.address = form.address.data
            employee.manager = form.manager.data
            employee.age = form.age.data
            db.session.commit()
            logger.info('employees profile shown from db')
            flash('You have successfully edited an employee.')
            return redirect(url_for('admin.list_employees1'))
    '''
@admin.route('/employees/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    lst = redisClient.lrange('c', -float('Inf'), float('Inf'))
    employee = Employee.query.get_or_404(current_user.id)
    for x in lst:
        print(pickle.loads(x))

    if x in lst:
        if pickle.loads(x)==employee:
            logger.info('employees profile shown from redis')
            return redirect(url_for('admin.view_profile_redis'))
        else:
            redisClient.lpush('c', pickle.dumps(employee))
            logger.info('employees profile shown from redis')
            return redirect(url_for('admin.view_profile_redis'))

    return render_template('admin/employees/profile.html',action="edit",
                           employee=employee,
                           title='Edit Employee')


@admin.route('/employees/profile_redis', methods=['GET', 'POST'])
@login_required
def view_profile_redis():
    id='e' + str(current_user.id)
    val = redisClient.hmget(id, 'name', 'designation', 'manager','age')
    return render_template('admin/employees/profile_redis.html',action="edit",id=id,
                           val=val,title='Edit Employee')



@admin.route('/employees/profile1', methods=['GET', 'POST'])
@login_required
def view_profile_admin():
    check_admin()
    employee = Employee.query.get_or_404(current_user.id)

    form = UpdateFormAdmin(obj=employee)
    if form.validate_on_submit():
        employee.email = form.email.data
        employee.name = form.name.data
        employee.designation = form.designation.data
        employee.address = form.address.data
        employee.age = form.age.data
        db.session.commit()
        body = {'id':employee.id,'name': employee.name,'designation': employee.designation,'manager': employee.manager,'age': employee.age}

        #keys = redisClient.keys()
        id='e'+str(employee.id)
        #for i in keys:
        if not redisClient.exists(id):
            es.index(index='contents2', doc_type='title', id=employee.id, body=body)
            redisClient.hmset('e' + str(employee.id), body)

        else:
            #es.update(index='contents1', doc_type='title', id=employee.id, body=body)
            redisClient.hmset('e' + str(employee.id), body)
        flash('You have successfully edited admins profile')


        return redirect(url_for('admin.list_employees'))

    return render_template('admin/employees/profile1.html',action="edit",
                           employee=employee, form=form,
                           title='Edit Employee')


@admin.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    check_admin()
    form = EmployeeAddForm()
    if form.validate_on_submit():
       #emp=str(form.manager.data)[11:-1]
       #print(emp)
       #manager = Employee.query.filter_by(name=emp).first()
       employee = Employee(email=form.email.data,name=form.name.data,
                            designation=form.designation.data,
                            salary=form.salary.data,
                            address=form.address.data,
                            manager=str(form.manager.data)[11:-1],
                            pNumber=form.pNumber.data,
                            password=form.password.data,
                            age=form.age.data,isManager=form.isManager.data)
       try:
           db.session.add(employee)
           db.session.commit()
           body = {'id':employee.id,'name': employee.name,'designation': employee.designation,'manager':employee.manager,'age':employee.age}
           redisClient.lpush('c', pickle.dumps(employee))
           es.index(index='contents2', doc_type='title', id=employee.id, body=body)
           redisClient.hmset('e' + str(employee.id), body)
           logger.info('added an employee')
           #redisClient.expire('e' + str(employee.id), 50)
           flash('You have successfully added an employee.')
           return redirect(url_for('admin.list_employees'))
       except Exception as e:
           flash(e)
    return render_template('admin/employees/add.html',form=form)

@admin.route('/employees/show_details/<int:id>')
@login_required
def show_details(id):
    check_admin()
    employee = Employee.query.get_or_404(id)
    logger.info('employees details shown')
    return render_template('admin/employees/show_details.html',
                           employee=employee,
                           title='Show Details')


@admin.route('/employees/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_employee(id):

    check_admin()

    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    employees=Employee.query.all()
    es.delete(index='contents2', doc_type='title', id=employee.id)
    redisClient.delete('e'+str(employee.id))
    logger.info('employee deleted')
    flash('You have successfully deleted the employee.')
    return redirect(url_for('admin.list_employees'))

    return render_template('admin/employees/employees.html',
                           employees=employees, title='Employees')



@admin.route('/employees/assessment', methods=['GET', 'POST'])
@login_required
def give_assessment():
    check_manager()
    form = AssessmentForm()
    if form.validate_on_submit():
        name=str(form.name.data)[11:-1]
        print name
        employee=Employee.query.filter_by(name=name).first()
        print employee
        employee.assessment=form.example.data
        try:
            db.session.commit()
            logger.info('assessment given ')
            flash('You have successfully submitted the assessment.')
            return redirect(url_for('admin.list_employees1'))
        except Exception as e:
            logger.error('assesment cannot be given')
            print str(e)
    return render_template('admin/employees/assessment.html',
                            form=form, title='Assessment')

@admin.route('/employees/feedback', methods=['GET', 'POST'])
@login_required
def give_feedback():
    name=current_user.manager
    employee=Employee.query.filter_by(name=name).first()
    form = FeedbackForm(obj=employee)
    if form.validate_on_submit():

        employee.feedback=form.feedback.data
        try:
            db.session.commit()
            logger.info('feedback given')
            flash('You have successfully submitted the feedback.')
            return redirect(url_for('admin.list_employees1'))
        except Exception as e:
            logger.error('feedback cannot be given')
            print str(e)
    return render_template('admin/employees/give_feedback.html',
                            form=form,
                           title='Feedback',name=current_user.manager,action="edit")


@admin.route('/employees/view_assessment', methods=['GET', 'POST'])
@login_required
def view_assessment():
    employee=Employee.query.filter_by(name=current_user.name).first()
    logger.info('assesment viewed')
    return render_template('admin/employees/show_assessment.html',
                           title='Assessment',employee=employee)


@admin.route('/employees/view_feedback', methods=['GET', 'POST'])
@login_required
def view_feedback():
    employee=Employee.query.filter_by(name=current_user.name).first()
    logger.info('feedback viewed')
    return render_template('admin/employees/show_feedback.html',
                           title='Assessment',employee=employee)


class holidays1(object):
    def __init__(self, name, price):
        self.name = name
        self.price = price


@admin.route('/holidaylist')
@login_required
def holidays():
    #logged_in=current_user
    #leave=Leave.query.filter_by(id=logged_in).first()
    #leave=leave.leave_status
    in_holidays = [
    holidays1('26-01-2019','Republic Day India'),
    holidays1('21-03-2019', 'Holi'),
    holidays1('1-05-2019', 'Maharashtra Day'),
    holidays1( '15-08-2019','Independence Day India'),
    holidays1 ('6-09-2019', 'Gauri Poojan'),
     holidays1( '2-10-2019', 'Gandhi Jayanti'),
     holidays1('29-10-2019', 'Bhaubeej')
    ]

    return render_template('admin/employees/holidays.html',in_holidays=in_holidays)


@login_required
@admin.route('/leave',methods=['GET','POST'])
def leave_app():
    logged_in=current_user.name
    employee=Employee.query.filter_by(name=logged_in).first()
    form = LeaveForm()
    if request.method=='POST' and form.validate_on_submit():
        d0 = form.dt.data
        d1 = form.dt1.data
        delta = d1 - d0
        if delta.days > 4:
            flash('balance is less')
        else:
            days=4-delta.days
            leave = Leave(name=employee.name,date_from=form.dt.data,date_to=form.dt1.data,days=days,leave_status='pending')
            try:
                db.session.add(leave)
                db.session.commit()
                logger.info('leave added')
                flash('You have successfully applied new leave.')
                return redirect(url_for('admin.list_leaves'))
            except:
                logger.error('leave cannot be added')
                flash('Error: cannot apply already exists.')



    return render_template('admin/employees/leaves.html', form=form)



@admin.route('/leave_list', methods=['GET', 'POST'])
@login_required
def list_leaves():

    emp_leave = Leave.query.filter_by(name=current_user.name).all()

    return render_template('admin/employees/leaves_list.html',
                           leaves=emp_leave, title="Leaves")



@admin.route('/leave_grant', methods=['GET', 'POST'])
@login_required
def leave_grant():
    check_manager()
    logged_in=current_user.name
    employee = Employee.query.filter_by(manager=logged_in).all()
    emp_on_leave=[]
    for emp in employee:
        l1=Leave.query.filter_by(name=emp.name).all()
        for leave in l1:
            if  leave.leave_status=='pending':
                emp_on_leave.append(leave)


    return render_template('admin/departments/leaves.html',
                           leaves=emp_on_leave, title="Leaves")


@admin.route('/leave_confirm/<int:id>', methods=['GET', 'POST'])
@login_required
def confirm_leave(id):
    check_manager()
    leave = Leave.query.get_or_404(id)
    leave.leave_status='approved'
    db.session.commit()
    flash('You have successfully approved a leave.')
    return redirect(url_for('admin.leave_grant'))



@admin.route('/leave_reject/<int:id>', methods=['GET', 'POST'])
@login_required
def reject_leave(id):
    check_manager()
    leave = Leave.query.get_or_404(id)
    leave.leave_status='rejected'
    db.session.commit()
    flash('You have successfully rejected a leave.')
    return redirect(url_for('admin.leave_grant'))


@admin.route('/leaves/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def del_leave(id):
    leave = Leave.query.get_or_404(id)
    if leave.leave_status=='pending':
        try:
            db.session.delete(leave)
            db.session.commit()
            logger.info('leave delted')
            flash('You have successfully withdrawn a leave.')
        except Exception as e:
            logger.error('levae cannot be deleted')
            flash("cannot delete")
    return redirect(url_for('admin.list_leaves'))

english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")

@admin.route('/help', methods=['GET', 'POST'])
@login_required
def help():
    if request.method=='POST':
        english_bot.set_trainer(ListTrainer)
        for _file in os.listdir('app/chats'):
            chats=open('app/chats/'+_file,'r').readlines()
            english_bot.train(chats)
        return redirect(url_for('admin.get_bot_response'))
    return render_template("admin/employees/index.html")

@admin.route('help/get')
@login_required
def get_bot_response():
        english_bot.set_trainer(ListTrainer)
        for _file in os.listdir('app/chats'):
            chats=open('app/chats/'+_file,'r').readlines()
            english_bot.train(chats)
        userText = request.args.get('msg')
        ans=(english_bot.get_response(userText))
        with open("log.txt", "a") as fh:
            fh.write("{user}: {message}\nBot: {reply}".format(
            user=current_user.name,
            message=userText,
            reply=ans))
        if userText=='hi':
             return 'Hello'
        if ans.confidence < 0.6:
            return 'sorry i didnt understand'
        return str(ans)





