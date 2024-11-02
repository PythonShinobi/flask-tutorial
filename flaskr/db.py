import click
import sqlite3

from datetime import datetime
from flask import current_app, g

def init_app(app):
    # Tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # Adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)


def init_db():
    db = get_db()

    # Opens a file relative to the flaskr package.
    with current_app.open_resource('schema.sql') as file:
        script = file.read().decode('utf-8')
        db.executescript(script)


# get_db will be called when the application has been created and 
# is handling a request, so current_app can be used.
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Tells the connection to return rows that behave like dicts. 
        # This allows accessing the columns by name.
        g.db.row_factory = sqlite3.Row

    return g.db


# Defines a command line command called init-db that calls the init_db function 
# and shows a success message to the user.
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Tells Python how to interpret timestamp values in the database.
sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)