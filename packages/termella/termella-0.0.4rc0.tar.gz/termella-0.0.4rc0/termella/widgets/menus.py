import sys
from ..core import Text
from ..input.listener import InputListener
from ..ansi import CURSOR_HIDE, CURSOR_SHOW, CURSOR_UP, CLEAN_LINE

def select(options, prompt="Select an option:", color="cyan", marker=">"):
    """
    Interactive selection menu using arrow keys.

    Args:
        options (list): List of string options.
        prompt (str): The question to ask.

    Returns:
        str: The selected option string.
    """
    listener = InputListener()
    idx = 0
    n = len(options)

    sys.stdout.write(CURSOR_HIDE)
    print(Text(prompt).style(styles="bold"))

    try:
        while True:
            # Render Options
            for i, opt in enumerate(options):
                # Clear line to ensure clean redraw
                sys.stdout.write(CLEAN_LINE)
                if i == idx:
                    # Highlight selected
                    print(Text(f"{marker} {opt}").style(color=color, styles="bold"))
                else:
                    # Dim unselected
                    print(Text(f"  {opt}").style(styles="dim"))
                
            # Wait for Input
            key = listener.read_key()
            if key == 'UP': idx = (idx - 1) % n
            elif key == 'DOWN': idx = (idx + 1) % n
            elif key == 'ENTER': return options[idx]
            elif key == 'ESC': return None

            # Move Cursor Back Up to redraw
            # We move up 'n' lines
            sys.stdout.write(f"\r{CURSOR_UP * n}")

    except KeyboardInterrupt:
        return None
    finally:
        sys.stdout.write(CURSOR_SHOW)
        print()

def checkbox(options, prompt="Select options (Space to toggle):", color="green", marker=">"):
    """
    [New in v0.0.4b] Multi-selection menu.

    Args:
        options (list): Options to choose from.
    Returns:
        list: A list of the selected option strings.
    """
    listener = InputListener()
    idx = 0
    n = len(options)
    selected_indices = set()

    sys.stdout.write(CURSOR_HIDE)
    print(Text(prompt).style(styles="bold"))

    try:
        while True:
            for i, opt in enumerate(options):
                sys.stdout.write(CLEAN_LINE)

                # Determine visual state
                is_focused = (i == idx)
                is_checked = (i in selected_indices)
                box = "[x]" if is_checked else "[ ]"
                cursor = marker if is_focused else " "
                # Render
                line_str = f"{cursor} {box} {opt}"

                if is_focused:
                    # Highlight the active line (cyan for focus)
                    print(Text(line_str).style(color="cyan", styles="bold"))
                elif is_checked:
                    # Highlight checked items that aren't focused (green)
                    print(Text(line_str).style(color=color))
                else:
                    # Dim unchecked, unfocused items
                    print(Text(line_str).style(styles="dim"))

            key = listener.read_key()
            if key == 'UP': idx = (idx - 1) % n
            elif key == 'DOWN': idx = (idx + 1) % n
            elif key == 'SPACE':
                # Toggle selection
                if idx in selected_indices: selected_indices.remove(idx)
                else: selected_indices.add(idx)
            elif key == 'ENTER':
                return [options[i] for i in sorted(list(selected_indices))]
            elif key == 'ESC':
                return []

            sys.stdout.write(f"\r{CURSOR_UP * n}")

    except KeyboardInterrupt:
        return []
    finally:
        sys.stdout.write(CURSOR_SHOW)
        print()