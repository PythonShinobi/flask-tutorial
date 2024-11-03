from flaskr import create_app

# Test that the app's configuration is correctly set up.
def test_config():
    # Check that the app is not in testing mode by default.
    assert not create_app().testing

    # Check that when 'TESTING' is set to True, the app is in testing mode.
    assert create_app({'TESTING': True}).testing


# Test a simple route in the app to confirm it returns the expected output.
def test_hello(client):
    # Use the test client to send a GET request to the '/hello' route.
    response = client.get('/hello')

    # Check if the response data matches the expected string 'Hello, World!'.
    # The response data is in bytes, so we use `b'...'` to compare.
    assert response.data == b'Hello, World!'
