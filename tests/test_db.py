import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        # test if get_db() returns the same object each time
        db = get_db()
        assert db is get_db()

    # ensure the connection is closed outside application context
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    # use fixture to replace call to init_db() with fake_init_db()
    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    # call 'init-db' command with fixture defined in conftest.py
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
