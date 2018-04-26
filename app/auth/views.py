from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import auth
from forms import LoginForm, RegistrationForm
from .. import db
from ..models import User

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            password=form.password.data
            )
        db.session.add(user)
        db.session.commit()
        flash('Success')

        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('home.media', category_filter='addons'))
        else:
            flash('Invalid name or password')
    return render_template('auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout Success!')

    return redirect(url_for('auth.login'))

