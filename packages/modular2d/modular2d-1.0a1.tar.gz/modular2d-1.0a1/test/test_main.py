"""
main.py

This script demonstrates the usage of the modular2d package.
It shows how to:
- Import the package and modules
- Use ListFormatter to print 2D tables
- Convert a dictionary into a formatted table
- Iterate through all available border styles
"""
try: import modular2d
except ImportError:
    import sys
    import os

    # Add the parent directory to sys.path so Python can find 'modular2d'
    # This is needed if running the script directly, outside of the package
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    # Import the modular2d package
    import modular2d

# Import specific modules/classes from the package
from modular2d import modulate as m
from modular2d import *  # Import everything in __all__ (ListFormatter, Border, ALL, etc.)

def run():
    """
    Run the demonstration of modular2d.

    This function:
    - Prints the package version
    - Creates ListFormatter instances for all available borders
    - Prints sample 2D table data
    - Prints a formatted dictionary as a table
    - Adds a disclaimer about the sample data
    """

    # Print the version of the modular2d package
    print("Version: " + modular2d.__version__)
    print()  # Blank line for spacing

    # Create a ListFormatter instance for each available border
    formatters = [ListFormatter(border=b) for b in ALL]

    # Iterate through each formatter (each with a different border style)
    for f in formatters:
        # Print the sample Border
        print(f.B)
        print() # Blank line for spacing
        
        # Print a table using the sample 2D data from test_data()
        print(f.format(f.test_data()))
        print()  # Add spacing between tables

        # Print a table generated from a test dictionary
        # Uses the formatter 'f' to render the table
        print(m.format_dictionary(m.get_test_dict(), formatter=f))
        print()  # Add spacing between tables

    # Print a disclaimer about the sample names
    print(
        "**All the names are imagined and do not taken from real identity. "
        "If matched, it is a pure coincidence.**"
    )

# Standard Python boilerplate to ensure this script runs only
# if executed directly, not when imported as a module
if __name__ == "__main__":
    run()