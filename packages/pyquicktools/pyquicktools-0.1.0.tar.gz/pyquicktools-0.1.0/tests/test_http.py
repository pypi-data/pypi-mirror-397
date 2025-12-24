import pytest
from pyquicktools import get


def test_get_success():
    r = get("https://jsonplaceholder.typicode.com/posts/1")
    assert r.status_code == 200
    assert "userId" in r.json()


def test_get_retry_fail():
    with pytest.raises(Exception):
        get("https://httpstat.us/500", retries=1)