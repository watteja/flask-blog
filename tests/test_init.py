from dailypush import create_app


def test_config():
    """
    Test create_app without passing test config.

    Makes sure that testing is by default off, and works. More info:
    https://flask.palletsprojects.com/en/2.2.x/api/#flask.Flask.test_client
    """
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


"""
def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"
"""


def test_init_db_command(runner, monkeypatch):
    called = False

    def fake_init_db():
        nonlocal called
        called = True

    # use fixture to replace call to init_db() with fake_init_db()
    monkeypatch.setattr("dailypush.init_db", fake_init_db)
    # call 'init-db' command with fixture defined in conftest.py
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert called
