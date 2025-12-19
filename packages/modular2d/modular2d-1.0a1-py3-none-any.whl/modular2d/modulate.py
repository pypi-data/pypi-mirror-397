"""
modulate.py

This module provides utilities for formatting structured Python data
into visually aligned text tables.

Main components:
- ListFormatter: formats 2D list/tuple data into a bordered table
- __formattoline: flattens nested list/tuple structures into a single line
- format_dictionary: converts a dictionary into a 2-column table

The module depends on a `border` module that provides:
- Border class
- get_random() factory
- Border.build(widths) → (top, mid, bottom)
"""

from typing import Iterable

# Attempt relative import when used inside a package
# Fallback to absolute import when used as a standalone script
try:
    from . import border as b
except Exception:
    import border as b


class ListFormatter:
    """
    Formats 2D list/tuple data into a bordered text table.
    """

    def __init__(self, *, border:b.Border=b.get_random()):
        """
        Create a ListFormatter instance.

        border:
            Expected to be a Border object.
            If not, a random border is selected automatically.
        """

        # Validate border instance
        if not isinstance(border, b.Border):
            border = b.get_random()

        # Store the border for later use
        self.B = border

    def format(self, data:Iterable[Iterable[object]], *, hasHeader:bool=True) -> str:
        """
        Convert 2D data into a formatted table string.

        data:
            A list or tuple of rows, where each row is a list or tuple.

        hasHeader:
            If True, the first row is treated as a header and
            a separator is drawn after it.
        """

        # Ensure hasHeader behaves strictly as boolean
        if not isinstance(hasHeader, (int, bool)):
            raise ValueError(
                f"Invalid literal for type boolean, 'hasHeader' ≠ '{hasHeader}'"
            )
        hasHeader = bool(hasHeader)

        # Data must be iterable
        if not isinstance(data, (list, tuple)):
            raise TypeError("Data should be atleast a sequence.")

        # Convert to list for mutation
        data = list(data)

        # Determine maximum column count
        width = max(len(row) for row in data)

        # Normalize rows and validate contents
        for r in range(len(data)):

            # Each row must itself be iterable
            if not isinstance(data[r], (list, tuple)):
                raise TypeError("Data should be a 2D array.")

            # Convert row to list
            data[r] = list(data[r])
            w = len(data[r])

            # Validate each cell
            for i in range(w):

                # Disallow nested containers
                if isinstance(data[r][i], (list, tuple, dict)):
                    raise ValueError(
                        f"Data cannot be a {type(data[r][i])} "
                        f"at row={r+1} column={i+1}."
                    )

                # Convert cell to string for rendering
                data[r][i] = str(data[r][i])

            # Pad rows with fewer columns
            for _ in range(width - w):
                data[r].append("")

        # Calculate maximum width per column
        width = [
            len(max(column, key=len))
            for column in list(zip(*data))
        ]

        # Generate table borders
        top, mid, bot = self.B.build(width)

        # Begin assembling output
        table = top + "\n"

        # Render each row
        for row in data:
            line = self.B.v

            # Render each cell with padding
            for i in range(len(row)):
                line += (
                    f" {row[i]} "
                    + " " * (width[i] - len(row[i]))
                    + self.B.v
                )

            table += line + "\n"

            # Insert header separator only once
            if hasHeader:
                hasHeader = False
                table += mid + "\n"

        # Append bottom border
        table += bot

        return table

    def test_data(self) -> list[list[object]]:
        """
        Return sample 2D data for testing and demonstration.
        ** All the names are imagined and do not taken from real identity. If matched, it is a pure coinsidence. **
        """

        return [
            ["ID", "Name", "Post", "Mobile"],
            ["001", "Aarav Sharma", "Manager", "9000010001"],
            ["002", "Ishita Verma", "Developer", "9000010002"],
            ["003", "Rohan Mehta", "Designer", "9000010003"],
            ["004", "Ananya Gupta", "HR Executive", "9000010004"],
            ["005", "Kabir Singh", "Data Analyst", "9000010005"],
            ["006", "Neha Kapoor", "Project Lead", "9000010006"],
            ["007", "Arjun Malhotra", "QA Engineer", "9000010007"],
            ["008", "Pooja Nair", "UI/UX Designer", "9000010008"],
            ["009", "Siddharth Jain", "Backend Engineer", "9000010009"],
            ["010", "Meera Iyer", "Content Writer", "9000010010"],
            ["011", "Vikram Rao", "DevOps Engineer", "9000010011"],
            ["012", "Sneha Kulkarni", "Business Analyst", "9000010012"],
            ["013", "Aditya Bose", "Product Manager", "9000010013"],
            ["014", "Kavya Choudhary", "Marketing Lead", "9000010014"],
            ["015", "Rahul Pandey", "Support Engineer", "9000010015"],
        ]


def __formattoline(lst, e=""):
    """
    Convert nested list/tuple structures into a single formatted line.

    Raises ValueError if a dictionary is encountered at any depth.
    """

    # Disallow dictionaries entirely
    if isinstance(lst, dict):
        raise ValueError(e)

    # Handle list/tuple recursively
    if isinstance(lst, (list, tuple)):
        lst = list(lst)
        line = ""

        for i in range(len(lst)):
            item = ""

            # Recursively format nested sequences
            if isinstance(lst[i], (list, tuple)):
                item += f"({__formattoline(lst[i])})"

            # Explicit dictionary rejection
            elif isinstance(lst[i], dict):
                raise ValueError(e)

            # Convert atomic values to string
            else:
                item += str(lst[i])

            line += item

            # Append separator except after last element
            if i < len(lst) - 1:
                line += ", "

        return line

    # Base case: return string representation
    else:
        return str(lst)


def format_dictionary(data:dict, *, formatter:ListFormatter=ListFormatter(border=b.get_random()), hasHeader:bool=False) -> str:
    """
    Convert a dictionary into a formatted table.

    Keys become the first column.
    Values are flattened into a single line using __formattoline.
    """

    # Initialize formatter
    if not isinstance(formatter, ListFormatter):
        formatter = ListFormatter(border=b.get_random())
    f = formatter

    # Input must be a dictionary
    if not isinstance(data, dict):
        raise TypeError(f"Cannot parse {type(data)}")

    keys = list(data.keys())

    # Prepare table rows
    lst = [] if hasHeader else [["ID", "Info"]]

    for k in keys:

        # Keys must be atomic values
        if isinstance(k, (list, tuple, dict)):
            raise ValueError(f"The key cannot be {type(k)}")

        # Append formatted key-value pair
        lst.append([
            str(k),
            __formattoline(data[k], f"Found another dictionary at '{k}'")
        ])

    # Always treat first row as header internally
    return f.format(lst, hasHeader=True)

def get_test_dict() -> dict:
    """
        Return sample Dictionary data for testing and demonstration.
        ** All the names are imagined and do not taken from real identity. If matched, it is a pure coinsidence. **
     """
    return {
        1: ["Alice", ("Developer", "Backend"), 25],
        2: ["Bob", ("Designer", "UI/UX"), 23],
        3: ["Charlie", ["Manager", ("Team A", "Team B")], 30],
        4: ["Diana", ("Analyst",), ["Finance", "Risk"]],
        5: ["Ethan", ["Intern", ("ML", "AI")], 21],
        6: ["Fiona", ("HR", "Recruitment"), ["Onboarding", "Training"]],
        7: ["George", ["DevOps", ("AWS", "Docker")], 28],
        8: ["Hannah", ("Writer", "Content"), ["Blogs", "Docs"]],
        9: ["Ian", ["Support", ("Level 1", "Level 2")], 26],
        10: ["Julia", ("Product", "Strategy"), ["Roadmap", "Vision"]],
    }