from flaskr import create_app


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
