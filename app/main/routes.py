from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import get_locale
from guess_language import guess_language
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post
from app.translate import translate_post


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    template = 'index.html'
    title = 'Home'
    form = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_post().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    if not form.validate_on_submit():
        return render_template(template, title=title, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)
    language = guess_language(form.post.data)
    if language == 'UNKNOWN' or len(language) > 5:
        language = ''
    post = Post(author=current_user, body=form.post.data, language=language)
    db.session.add(post)
    db.session.commit()
    flash('Your post is now live')
    return redirect(url_for('main.index'))


@bp.route('/explore')
def explore():
    template = 'index.html'
    title = 'Explore'
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template(template, title=title, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    template = 'user.html'
    title = user.username
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template(template, title=title, user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
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
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself.')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!')
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself.')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}!')
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    translated_text = {
        'text': translate_post(request.form['text'], request.form['to_language']),
    }
    return jsonify(translated_text)