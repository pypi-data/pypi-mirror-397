from ..core import Text

def panel(text, color="white", title=None):
    """
    Creates a simple ASCII box around text.
    """
    text = str(text)
    lines = text.split("\n")
    width = max(len(line) for line in lines) + 2
    tl, tr, bl, br, h, v= "┌", "┐", "└", "┘", "─", "│"

    t_str = f" {title} " if title else ""
    top = h * (width - len(t_str))

    print(Text(f"{tl}{t_str}{top}{tr}").style(color))
    for line in lines:
        print(Text(f"{v}{line.ljust(width)}{v}").style(color))
    print(Text(f"{bl}{h * width}{br}").style(color))