import os
import pytest
import tempfile

from flaskr import create_app
from flaskr.db import get_db, init_db

class AuthActions(object):
    # The AuthActions class is a helper for performing authentication-related actions in tests.
    # It allows tests to log in and log out using a consistent interface.
    
    def __init__(self, client):
        # Initialize the AuthActions instance with the test client.
        # `client` is a test client (from Flask) that allows simulating HTTP requests.
        self._client = client

    def login(self, username='test', password='test'):
        # Define a `login` method that simulates a POST request to the login route.
        # The default `username` and `password` values are set to 'test' for convenience.
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        # Define a `logout` method that simulates a GET request to the logout route.
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    # `auth` is a fixture that provides an instance of the `AuthActions` class.
    # It takes `client` (a Flask test client fixture) and passes it to `AuthActions`.
    # This allows tests to use `auth.login()` and `auth.logout()` for authentication actions.
    return AuthActions(client)


# Open and read the contents of the 'data.sql' file, which contains 
# test database data. This data will be loaded into the database 
# each time the test app is initialized.
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as file:
    _data_sql = file.read().decode('utf8')


# This fixture creates and configures a new app instance for each test.
@pytest.fixture
def app():
    # Create a temporary file to act as a mock database for testing.
    db_fd, db_path = tempfile.mkstemp()

    # Create the Flask app instance with testing configuration.
    app = create_app({
        'TESTING': True,        # Enable testing mode (disables error catching).
        'DATABASE': db_path,    # Use the temporary database path.
    })

    # Within the app context, initialize the database and load test data.
    with app.app_context():
        init_db()               # Initialize the database schema.
        get_db().executescript(_data_sql)  # Load the test data into the database.

    # Provide the app instance to the tests, and then clean up.
    yield app

    # Clean up: Close the database file and remove it from the file system.
    os.close(db_fd)
    os.unlink(db_path)


# This fixture provides a test client for the app, allowing tests 
# to simulate HTTP requests.
@pytest.fixture
def client(app):
    return app.test_client()


# This fixture provides a test CLI runner, which lets tests call 
# CLI commands in the app.
@pytest.fixture
def runner(app):
    return app.test_cli_runner()
