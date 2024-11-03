import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    # Check if the registration page loads successfully with a GET request.
    assert client.get('/auth/register').status_code == 200

    # Send a POST request with username and password to register a new user.
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )

    # Verify that after registration, the user is redirected to the login page.
    assert response.headers["Location"] == "/auth/login"

    # Check within the application context if the new user is saved in the database.
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    # Send a POST request with varying inputs to test validation messages.
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )

    # Check if the expected validation error message appears in the response data.
    assert message in response.data


def test_login(client, auth):
    # Check if the login page loads successfully with a GET request.
    assert client.get('/auth/login').status_code == 200

    # Attempt to log in with default test credentials.
    response = auth.login()
    
    # Verify that after a successful login, the user is redirected to the home page.
    assert response.headers["Location"] == "/"

    # Use a client context to access the session and global user information.
    with client:
        client.get('/')  # Access the home page.
        
        # Check that the session contains the user ID of the logged-in user.
        assert session['user_id'] == 1
        
        # Verify that the global user object contains the correct username.
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),  # Test case for an incorrect username.
    ('test', 'a', b'Incorrect password.'),  # Test case for an incorrect password.
))
def test_login_validate_input(auth, username, password, message):
    # Attempt to log in with the given username and password.
    response = auth.login(username, password)
    
    # Check that the expected error message is returned in the response data.
    assert message in response.data


def test_logout(client, auth):
    # Log in using the auth fixture.
    auth.login()

    # Use a client context to test logout functionality.
    with client:
        # Call the logout method to log the user out.
        auth.logout()
        
        # Verify that the user ID is removed from the session after logging out.
        assert 'user_id' not in session
