#  pyquicktools

<div align="center">

![PyPI Version](https://img.shields.io/pypi/v/pyquicktools?color=blue&style=flat-square)
![Python Versions](https://img.shields.io/pypi/pyversions/pyquicktools?style=flat-square)
![License](https://img.shields.io/pypi/l/pyquicktools?style=flat-square)
![GitHub Stars](https://img.shields.io/github/stars/Suhani1234-5/pyquicktools?style=flat-square)
![Downloads](https://static.pepy.tech/personalized-badge/pyquicktools?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads)

**The Python utility toolbox you didn't know you needed — until now.**

*One package. Minimal dependencies. Maximum productivity.*

 **Perfect for GSoC, open-source contributors, backend engineers & interview projects**

Built with **real-world backend failures** in mind — not toy examples.

[Installation](#-installation) • [Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

##  Why pyquicktools?

Stop installing 5+ packages for basic Python tasks. **pyquicktools** combines the most-needed utilities into one lightweight, blazing-fast package:

**Auto-retry HTTP requests** with exponential backoff  
 **Colorized debug printing** with file/line tracking  
**Async retry support** for `aiohttp`  
 **Safe JSON parsing** that fixes common errors  
 **Minimal configuration** — works out of the box  

**Before pyquicktools:**
```bash
pip install requests tenacity simplejson pprint colorama
```

**After pyquicktools:**
```bash
pip install pyquicktools
```

---

## 📦 Installation

```bash
pip install pyquicktools
```

**Requirements:** Python 3.8+

---

##  Features

###  1. Auto-Retry HTTP Requests

Never lose data to flaky APIs again. Automatic retries with exponential backoff.

```python
from pyquicktools import get, post

# Auto-retry on failure (default: 3 retries)
response = get("https://api.example.com/data", retries=5, timeout=10)
print(response.json())

# Works with POST too
response = post(
    "https://api.example.com/submit",
    json={"name": "Suhani"},
    retries=3,
    retry_statuses=[429, 500, 502, 503]
)
```

**Features:**
-  Exponential backoff (1s → 2s → 4s → 8s)
-  Retry on specific status codes (429, 500, 502, 503)
-  Configurable timeout per request
-  Safe POST retries using **idempotency keys** (no accidental double writes)

---

###  2. Colorized Debug Print

Say goodbye to boring `print()` statements. Get beautiful, informative debug output.

```python
from pyquicktools import dprint

user = {"name": "Suhani", "age": 22}
items = ["laptop", "phone", "charger"]

dprint(user, items)
```

**Output:**
```
🐛 main.py:12 → [user={'name': 'Suhani', 'age': 22}] [items=['laptop', 'phone', 'charger']]
```

**Features:**
-  **Color-coded** output (variables in cyan, values in green)
-  **Automatic file + line number** tracking
-  **Named arguments** shown clearly
-  **Minimal configuration** — just replace `print()` with `dprint()`

**Advanced usage:**
```python
# Disable colors
dprint(data, color=False)

# Custom separator
dprint(x, y, z, sep=" | ")

# Show only values (no variable names)
dprint(user, items, show_names=False)

# File logging support (via standard print file argument)
dprint(error_data, file=open("debug.log", "a"))
```

---

###  3. Async HTTP Retry (aiohttp)

Supercharge your async code with automatic retries.

> ⚠️ **Note:** Async features require `aiohttp`.  
> Install with: `pip install pyquicktools aiohttp`

```python
import asyncio
from pyquicktools import async_get

async def fetch_data():
    # Auto-retry async requests
    data = await async_get(
        "https://api.example.com/data",
        retries=3,
        timeout=5
    )
    print(data)
    return data

asyncio.run(fetch_data())
```

**Features:**
-  **Async/await** support with `aiohttp`
-  Same retry logic as sync version
-  Perfect for high-throughput applications

---

###  4. Safe JSON Loading

Parse JSON that's almost-but-not-quite valid. Fixes common errors automatically.

```python
from pyquicktools import load_json

# Handles trailing commas, comments, NaN, Infinity
data = load_json("""
{
    "name": "Suhani", // This is a comment
    "age": "22",      // String will be converted to int
    "score": NaN,     // Will be converted to None
}
""")

print(data["age"])  # Output: 22 (int, not string!)
```

**Auto-fixes:**
-  Trailing commas in arrays/objects
-  JavaScript-style comments (`//` and `/* */`)
-  `NaN` and `Infinity` values
- Optional smart typecasting for numeric strings

---

##  Quick Start

### Example 1: Resilient API Calls

```python
from pyquicktools import get, dprint

try:
    response = get(
        "https://api.github.com/users/Suhani1234-5",
        retries=3,
        timeout=5
    )
    data = response.json()
    dprint(data["name"], data["public_repos"])
except Exception as e:
    dprint(f"Error: {e}", color=False)
```

---

### Example 2: Async Data Fetching

```python
import asyncio
from pyquicktools import async_get

async def fetch_multiple():
    urls = [
        "https://api.example.com/1",
        "https://api.example.com/2",
        "https://api.example.com/3"
    ]
    
    tasks = [async_get(url, retries=2) for url in urls]
    results = await asyncio.gather(*tasks)
    
    for data in results:
        print(data)

asyncio.run(fetch_multiple())
```

---

### Example 3: Parse Messy JSON

```python
from pyquicktools import load_json

# From API response with comments
messy_json = """
{
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},  // trailing comma
    ],
    "total": "100",  // Should be int
}
"""

data = load_json(messy_json)
print(type(data["total"]))  # <class 'int'>
```

---

##  Documentation

### `get(url, retries=3, timeout=5, retry_statuses=[429, 500, 502, 503], **kwargs)`

**Parameters:**
- `url` (str): Target URL
- `retries` (int): Max retry attempts (default: 3)
- `timeout` (int): Request timeout in seconds (default: 5)
- `retry_statuses` (list): HTTP status codes to retry on
- `**kwargs`: Additional arguments passed to `requests.get()`

**Returns:** `requests.Response` object

---

### `post(url, retries=3, timeout=5, retry_statuses=[429, 500, 502, 503], **kwargs)`

**Parameters:**
- `url` (str): Target URL
- `retries` (int): Max retry attempts (default: 3)
- `timeout` (int): Request timeout in seconds (default: 5)
- `retry_statuses` (list): HTTP status codes to retry on
- `**kwargs`: Additional arguments passed to `requests.post()`

**Returns:** `requests.Response` object

---

### `dprint(*args, color=True, sep=' ', show_names=True, **kwargs)`

**Parameters:**
- `*args`: Variables to print
- `color` (bool): Enable colored output (default: True)
- `sep` (str): Separator between arguments (default: ' ')
- `show_names` (bool): Show variable names (default: True)
- `**kwargs`: Additional arguments passed to built-in `print()` (including `file` for logging)

---

### `load_json(json_string, auto_typecast=True)`

**Parameters:**
- `json_string` (str): JSON string to parse
- `auto_typecast` (bool): Automatically convert string numbers to int/float (default: True)

**Returns:** Parsed Python dict/list

---

##  Advanced Usage

### Custom Retry Strategy

```python
from pyquicktools import get

response = get(
    "https://api.example.com/data",
    retries=5,
    retry_statuses=[429, 500, 502, 503, 504],
    timeout=10,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

---

### Logging with dprint

```python
from pyquicktools import dprint

# In production: disable colors for log files
with open("debug.log", "a") as log_file:
    dprint(error_data, color=False, file=log_file)
```

---

## 🤝 Contributing

We love contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/Suhani1234-5/pyquicktools.git
cd pyquicktools
pip install -e ".[dev]"
pytest
```

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Star History

If you find this project useful, please consider giving it a ⭐ on [GitHub](https://github.com/Suhani1234-5/pyquicktools)!

---

## Contact

**Suhani Garg**  
📧 suhanigarg59@gmail.com  
[GitHub](https://github.com/Suhani1234-5)

---

<div align="center">

**Made with ❤️ by Suhani Garg**

[⬆ Back to Top](#-pyquicktools)

</div>