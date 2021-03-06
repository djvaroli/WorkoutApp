from flask import render_template, current_app
from flask_babel import _
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[WorkoutApp] Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_confirm_email(user):
    token = user.get_confirm_email_token()
    send_email(_('[WorkoutApp] Confirm Your Email'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/confirm_email.txt',user=user,token=token),
               html_body=render_template('email/confirm_email.html',user=user,token=token))

def send_new_user_email(user):
    send_email(_('[WorkoutApp] New User Registration'),
               sender=current_app.config['ADMINS'][0],
               recipients=[current_app.config['ADMINS'][1]],
               text_body=render_template('email/new_user.txt', user=user),
               html_body=render_template('email/new_user.html', user=user))

def new_admin_email(user):
    send_email(_('[WorkoutA] Administrator Priviliges)'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/new_admin.txt',user=user),
               html_body=render_template('email/new_admin.html',user=user))