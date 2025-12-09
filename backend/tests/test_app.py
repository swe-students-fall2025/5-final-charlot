"""Test basic webpage"""


def test_homepage(test_client):
    """Test that homepage returns 200 response"""

    response = test_client.get("/")
    assert response.status_code == 200
