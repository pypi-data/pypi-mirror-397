import random as r

# border.py

class Border:
    """
    Represents a complete set of characters used to draw
    a text-based table border.
    """

    def __init__(
        self, *,
        tl:str="+", tm:str="+", tr:str="+",
        ml:str="+", mm:str="+", mr:str="+",
        bl:str="+", bm:str="+", br:str="+",
        v:str="|", h:str="-"
    ):
        # Top-left, top-middle, top-right corner characters
        self.tl = tl
        self.tm = tm
        self.tr = tr

        # Middle-left, middle-middle, middle-right junction characters
        self.ml = ml
        self.mm = mm
        self.mr = mr

        # Bottom-left, bottom-middle, bottom-right corner characters
        self.bl = bl
        self.bm = bm
        self.br = br

        # Vertical and horizontal line characters
        self.v = v
        self.h = h

    def build(self, width:list) -> str:
        """
        Construct the top, middle, and bottom border strings
        based on column widths.

        width:
            A list of integers representing column widths.

        Returns:
            (top, mid, bot) tuple of strings.
        """

        # Initialize border lines with left corner characters
        top = self.tl
        mid = self.ml
        bot = self.bl

        i = 0

        # Iterate through each column width
        for w in width:

            # Add horizontal lines with padding for each column
            top += (self.h * (w + 2))
            mid += (self.h * (w + 2))
            bot += (self.h * (w + 2))

            # Add column separators if not the last column
            if i < len(width) - 1:
                top += self.tm
                mid += self.mm
                bot += self.bm

            i += 1

        # Append right corner characters
        top += self.tr
        mid += self.mr
        bot += self.br

        return top, mid, bot
    
    def __str__(self):
        # Return a sample of empty table for check
        return self.tl + self.h + self.tm + self.h + self.tr + "\n" + self.v + " " + self.v +  " " + self.v + "\n" + self.ml + self.h + self.mm + self.h + self.mr + "\n" + self.v + " " + self.v +  " " + self.v + "\n" + self.bl + self.h + self.bm + self.h + self.br


# Default ASCII border using '+' '-' '|'
BORDER_ASCII = Border()

# ASCII border using a long horizontal dash as better merge
BORDER_ASCII_LONG = Border(
    tl="┌", tm="┬", tr="┐",
    ml="├", mm="┼", mr="┤",
    bl="└", bm="┴", br="┘",
    v="│", h="─"
)

# Collection of all available borders
ALL = [
    BORDER_ASCII,
    BORDER_ASCII_LONG
]


def get_random() -> Border:
    """
    Return a randomly selected Border instance
    from the predefined collection.
    """
    return ALL[r.randint(0, len(ALL) - 1)]