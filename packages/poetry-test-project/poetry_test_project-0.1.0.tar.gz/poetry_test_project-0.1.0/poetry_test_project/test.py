import pytest

# print hello world
print("Hello World")


@pytest.mark.test
def test_hello_world():
    assert "Hello World" == "Hello World"
