import json
import re

def _remove_comments(text):
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return text

def _remove_trailing_commas(text):
    return re.sub(r",\s*([}\]])", r"\1", text)

def _fix_nan_inf(text):
    return (
        text.replace("NaN", "null")
        .replace("Infinity", "null")
        .replace("-Infinity", "null")
    )

def _auto_cast(value):
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
    if isinstance(value, list):
        return [_auto_cast(v) for v in value]
    if isinstance(value, dict):
        return {k: _auto_cast(v) for k, v in value.items()}
    return value

def load_json(text: str):
    try:
        cleaned = _remove_comments(text)
        cleaned = _remove_trailing_commas(cleaned)
        cleaned = _fix_nan_inf(cleaned)
        data = json.loads(cleaned)
        return _auto_cast(data)
    except Exception as e:
        raise ValueError(f"Invalid JSON: {e}")
