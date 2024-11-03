import pytest
import sqlite3

from flaskr.db import get_db

# Test that the database connection is correctly created and closed.
def test_get_close_db(app):
    # Open an application context to simulate a request handling context.
    with app.app_context():
        # Retrieve a database connection and verify it returns the same connection
        # when `get_db()` is called again, indicating a single connection per request.
        db = get_db()
        assert db is get_db()  # Check that the same connection is returned.

    # After the context is exited, the database connection should be closed.
    # Attempting to use it now should raise a ProgrammingError.
    with pytest.raises(sqlite3.ProgrammingError) as e:
        # This line attempts to use the closed database connection, which should fail.
        db.execute('SELECT 1')

    # Check that the error message indicates the database connection is closed.
    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    # Define a Recorder class to keep track of whether our `fake_init_db` function is called.
    class Recorder(object):
        called = False  # Boolean flag to record if the function was called.

    # Define a fake version of `init_db` to replace the real one during testing.
    def fake_init_db():
        # When called, this function will set the `called` attribute to True.
        Recorder.called = True

    # Use monkeypatch to temporarily replace `init_db` in `flaskr.db` with `fake_init_db`.
    # This allows us to test whether `init_db` was triggered without actually initializing the database.
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)

    # Use the `runner` fixture to simulate running the CLI command `init-db`.
    result = runner.invoke(args=['init-db'])

    # Check if the command's output contains the expected success message "Initialized".
    assert 'Initialized' in result.output

    # Confirm that `fake_init_db` was called, indicating the command triggered `init_db`.
    assert Recorder.called
