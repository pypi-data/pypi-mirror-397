from pyquicktools import load_json


def test_safe_json():
    raw = """
    {
        "age": "20", // comment
        "score": NaN,
    }
    """
    data = load_json(raw)
    assert data["age"] == 20
    assert data["score"] is None
