from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    template = 'index.html'
    context = {
        'title': 'Home',
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
    return render_template(template, context=context)
