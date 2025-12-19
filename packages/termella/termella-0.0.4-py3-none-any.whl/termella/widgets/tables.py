from ..core import Text

def table(data, headers=None, border_color="white", align="left"):
    """
    Renders a list of lists as a table.

    Args:
        data (list): list of rows (e.g. [['A', 'B'], ['C', 'D']])
        headers (list): List of column titles.
    """
    if not data and not headers: 
        return

    if data:
        # Calculate column widths
        cols = len(data[0])
    else:
        cols = len(headers)

    if isinstance(align, str):
        aligns = [align.lower()] * cols
    else:
        aligns = [a.lower() for a in align] + ["left"] * (cols - len(align))

    widths = [0] * cols
    all_rows = ([] if not headers else [headers]) + (data if data else [])

    for row in all_rows:
        for i in range(min(len(row), cols)):
            widths[i] = max(widths[i], len(str(row[i])))

    def format_cell(content, width, alignment):
        content = str(content)
        if alignment == "right":
            return content.rjust(width)
        elif alignment == "center":
            return content.center(width)
        else: # left
            return content.ljust(width)

    # Formatting helpers
    def print_sep(left, mid, right, line):
        segments = [line * (w + 2) for w in widths]
        full_line = left + mid.join(segments) + right
        print(Text(full_line).style(border_color))

    # Top Border
    print_sep("┌", "┬", "┐", "─")

    # Headers
    if headers:
        row_str = "│"
        for i, cell in enumerate(headers):
            content = format_cell(cell, widths[i], aligns[i])
            row_str += f" {content} │"
        print(Text(row_str).style(border_color, styles="bold"))
        print_sep("├", "┼", "┤", "─")

    # Data
    if not data:
        total_width = sum(widths) + (cols * 3) - 1
        print(Text("│ " + "No Data".center(total_width) + " │").style(border_color, styles="dim"))
    else:
        for row in data:
            row_str = "│"
            for i in range(cols):
                cell = row[i] if i < len(row) else ""
                content = format_cell(cell, widths[i], aligns[i])
                row_str += f" {content} │"
            print(Text(row_str).style(border_color))

    # Bottom Border
    print_sep("└", "┴", "┘", "─")