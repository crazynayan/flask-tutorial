from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    template = 'index.html'
    title = 'Home'
    context = {
        'user': {
            'username': 'Nayan',
        },
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
    template = 'login.html'
    title = 'Sign In'
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template(template, title=title, form=form)
    # This is a POST request and the form is validated
    flash(f'Logged in as {form.username.data} (Remember me is: {form.remember_me.data})')
    return redirect(url_for('index'))
