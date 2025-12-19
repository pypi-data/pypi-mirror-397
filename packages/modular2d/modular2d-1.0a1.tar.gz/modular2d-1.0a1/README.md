# Modular2d

A lightweight Python library for formatting structured data into clean, visually aligned **text-based tables** using customizable borders.

Designed for terminal output, debugging, logging, and CLI applications.  
Pure Python. No external dependencies.

---

## Features

- Format 2D lists and tuples into bordered text tables
- Convert dictionaries into readable two-column tables
- Multiple border styles (ASCII and Unicode)
- Optional random border selection
- Safe input validation and clear errors
- Works in any terminal environment

---

## Installation

Clone the repository.
Install locally (editable mode):

```bash
pip install -e .
```

---

## Quick Start

Format a 2D list into a table:

```python
from modular2d import ListFormatter

data = [
    ["ID", "Name", "Role"],
    [1, "Alice", "Developer"],
    [2, "Bob", "Designer"]
]

formatter = ListFormatter()
print(formatter.format(data))
```

---

## Using Built-in Test Data

The package includes sample data for demonstration:

```python
from modular2d import ListFormatter

f = ListFormatter()
print(f.format(f.test_data()))
```

---

## Formatting Dictionaries

Dictionaries can be converted into readable tables where:
- Keys become the first column
- Values are flattened into a single line

```python
from modular2d.modulate import format_dictionary

data = {
    1: ["Alice", ("Developer", "Backend"), 25],
    2: ["Bob", ("Designer", "UI/UX"), 23]
}

print(format_dictionary(data))
```

Nested lists and tuples are flattened automatically.

---

## Border Styles

### Default ASCII Border

```python
from modular2d import BORDER_ASCII, ListFormatter

formatter = ListFormatter(border=BORDER_ASCII)
```

### Unicode Border

```python
from modular2d import BORDER_ASCII_LONG, ListFormatter

formatter = ListFormatter(border=BORDER_ASCII_LONG)
```

### Random Border

```python
from modular2d import ListFormatter

formatter = ListFormatter()
```

A random predefined border is selected automatically.

---

## Public API

The following symbols are part of the public API:

- `ListFormatter`
- `Border`
- `BORDER_ASCII`
- `BORDER_ASCII_LONG`
- `ALL`

---

## Version

```text
1.0.a
```

---

## License

MIT License  
See the LICENSE file for full text.

---

## Notes

- All example names and data are fictional
- No external libraries are required
- Intended for clarity, correctness, and terminal readability
