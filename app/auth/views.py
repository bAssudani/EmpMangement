import json
from os import abort

from oauthlib.oauth2 import WebApplicationClient
from google.auth.transport import requests
import requests
from flask import flash, redirect, render_template, url_for, logging, app, request, session
from flask_login import login_required, login_user, logout_user, current_user
from . import auth
from forms import LoginForm, RegistrationForm
from .. import db, get_google_provider_cfg, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from ..models import Employee



@auth.route('/login', methods=['GET', 'POST'])
def login():
    #form = LoginForm()
   # if form.validate_on_submit():
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        client = WebApplicationClient(GOOGLE_CLIENT_ID)

        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=request.base_url + "/callback",
            scope=["openid", "email", "profile"],
        )

        return redirect(request_uri)
        #employee = Employee.query.filter_by(email=form.email.data).first()
        #if employee is not None and employee.verify_password(
         #       form.password.data):

          #  login_user(employee)

           # logging.info('logged in')
            #if employee.is_admin:
            #    return redirect(url_for('home.admin_dashboard'))
            #else:
             #   return redirect(url_for('home.dashboard'))


        #else:
         #   flash('Invalid name or password.')


    #return render_template('auth/login.html', form=form, title='Login')

@auth.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_url = "https://accounts.google.com/o/oauth2/token"
    refresh_url = token_url
    client = WebApplicationClient(GOOGLE_CLIENT_ID)
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    employee = Employee.query.filter_by(email=users_email).first()
    login_user(employee)
    if employee.email=='bhavika301297@gmail.com':
        employee.is_admin=1
        return redirect(url_for("home.admin_dashboard"))
    else:
        return redirect(url_for("home.dashboard"))



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
