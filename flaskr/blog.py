from werkzeug.exceptions import abort
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


# The check_author argument is defined so that the function can be used to get a post 
# without checking the author. This would be useful if you wrote a view to show an individual 
# post on a page, where the user doesn’t matter because they’re not modifying the post.
def get_post(id, check_author=True):
    """Fetches a specific post from the database by id."""
    # The post is retrieved by joining the post and user tables (to get the username of the author).
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f'Post id {id} does not exist.')  # Not Found

    # If check_author is True and the current user (g.user) is not the 
    # author, it raises a 403 Forbidden error.
    if check_author and post['author_id'] != g.user['id']:
        abort(403)  # Forbidden

    return post


@bp.route('/')
def index():
    """Displays all blog posts."""
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Allows authenticated users to create a new blog post."""
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = None
        if not title:
            error = 'Title is required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post(title, body, author_id)'
                'VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()

            return redirect(url_for('blog.index'))
        
    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Allows the post author to edit an existing post."""
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        error = None
        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                'WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
        
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Allows the post author to delete a post."""
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))