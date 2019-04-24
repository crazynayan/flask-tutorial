from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    template = 'index.html'
    title = 'Home'
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_post().paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    if not form.validate_on_submit():
        return render_template(template, title=title, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)
    post = Post(author=current_user, body=form.post.data)
    db.session.add(post)
    db.session.commit()
    flash('Your post is now live')
    return redirect(url_for('index'))


@app.route('/explore')
def explore():
    template = 'index.html'
    title = 'Explore'
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template(template, title=title, posts=posts.items, next_url=next_url, prev_url=prev_url)


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
    template = 'register.html'
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


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    template = 'user.html'
    title = user.username
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template(template, title=title, user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    template = 'edit_profile.html'
    title = 'Edit Profile'
    form = EditProfileForm(current_user.username)
    if request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    if not form.validate_on_submit():
        return render_template(template, title=title, form=form)
    # POST request with form data validated
    current_user.username = form.username.data
    current_user.about_me = form.about_me.data
    db.session.commit()
    return redirect(url_for('user', username=current_user.username))


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself.')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!')
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself.')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}!')
    return redirect(url_for('user', username=username))

