from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    template = 'index.html'
    title = 'Home'
    context = {
        'posts': [
            {
                'author': {
                    'username': 'Nisha',
                },
                'body': 'Work is hectic!!',
            },
            {
                'author': {
                    'username': 'Suditi',
                },
                'body': 'Did you see the last episode of #got?',
            },
        ],
    }
    return render_template(template, title=title, context=context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    template = 'login.html'
    title = 'Sign In'
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template(template, title=title, form=form)
    # This is a POST request and the form is validated
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user=user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    template = 'registration.html'
    title = 'Registration'
    form = RegistrationForm()
    if not form.validate_on_submit():
        return render_template(template, title=title, form=form)
    # This is a POST request and the form is validated
    # Add the user
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Congratulations! You have been registered. Please login.')
    return redirect(url_for('login'))

