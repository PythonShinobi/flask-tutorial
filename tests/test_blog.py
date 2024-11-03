import pytest
from flaskr.db import get_db


def test_index(client, auth):
    # Verify that the homepage contains login and registration links when a user is not logged in.
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # Log in using the auth fixture and verify that the homepage now contains a logout link and post details.
    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',  # Path to create a new post
    '/1/update',  # Path to update the first post
    '/1/delete',  # Path to delete the first post
))
def test_login_required(client, path):
    # For each path, check that the user is redirected to the login page when they are not logged in.
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # Change the author of the post with ID 1 to a different user.
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    # Log in as the original user and verify they cannot modify another user's post.
    auth.login()
    assert client.post('/1/update').status_code == 403  # Check that update is forbidden
    assert client.post('/1/delete').status_code == 403  # Check that delete is forbidden
    # Verify that the current user does not see the edit link for the post.
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',  # Path to update the second post
    '/2/delete',  # Path to delete the second post
))
def test_exists_required(client, auth, path):
    # Log in and check that attempting to update or delete a non-existent post returns a 404 status.
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    # Log in and verify that the create post page loads successfully.
    auth.login()
    assert client.get('/create').status_code == 200
    # Post a new post with a title.
    client.post('/create', data={'title': 'created', 'body': ''})

    # Verify that the new post was added to the database.
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2  # Check that there are now 2 posts


def test_update(client, auth, app):
    # Log in and verify that the update post page loads successfully.
    auth.login()
    assert client.get('/1/update').status_code == 200
    # Update the title of the first post.
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    # Verify that the post's title was updated in the database.
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',  # Path to create a new post
    '/1/update',  # Path to update the first post
))
def test_create_update_validate(client, auth, path):
    # Log in and test that posting with empty title and body returns an error message.
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    # Log in and delete the first post.
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"  # Check that the user is redirected to the homepage after deletion

    # Verify that the post has been removed from the database.
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None  # Ensure the post no longer exists
