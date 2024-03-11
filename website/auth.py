from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user ,current_user
from website.models import Register
from website import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('loginemail')
        password = request.form.get('loginpassword')

        user = Register.query.filter_by(email=email).first()
        if user:
            if user.password == password and user.userrole == 0:
                if user.status == 1:
                    login_user(user, remember=True)
                    return redirect('studentdashboard')
                else:
                    flash("Student not verified!!!!!", category='error')
            elif user.password == password and user.userrole == 1:
                if user.status == 1:
                    login_user(user, remember=True)
                    return redirect('teacherdashboard')
                else:
                    flash("Teacher not verified!!!!!", category='error')
            elif user.password == password and user.userrole == 2:
                login_user(user, remember=True)
                return redirect('admindashboard')
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist', category='error')
    return render_template("login.html")







@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



