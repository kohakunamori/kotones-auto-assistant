import os
import ctypes
import shutil
import unicodedata
from typing import Optional

def _enable_windows_ansi():
    """
    On Windows, attempts to enable ANSI escape sequence processing.
    """
    if os.name == 'nt':
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
                return  # Failed to get console mode
            
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            
            if (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING) == 0:
                mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
                if kernel32.SetConsoleMode(handle, mode) == 0:
                    # Fallback for older systems
                    os.system('')
        except Exception:
            # Fallback for environments where ctypes fails (e.g., some IDE terminals)
            os.system('')

_enable_windows_ansi()

class Color:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    GRAY = '\033[90m'

def get_terminal_width(default=80):
    """Gets the width of the terminal."""
    # shutil.get_terminal_size is a high-level and more robust way
    return shutil.get_terminal_size((default, 24)).columns

def get_terminal_height(default=24):
    """Gets the height of the terminal."""
    return shutil.get_terminal_size((default, 24)).lines

def get_display_width(s: str) -> int:
    """Calculates the display width of a string, accounting for wide characters."""
    width = 0
    for char in s:
        # 'F' (Fullwidth), 'W' (Wide) characters take up 2 columns.
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def truncate_string(s: str, max_width: int) -> str:
    """Truncates a string to a maximum display width, handling wide characters."""
    if not s or max_width <= 0:
        return ""
        
    width = 0
    end_pos = 0
    for i, char in enumerate(s):
        # 'F' (Fullwidth), 'W' (Wide) characters take up 2 columns.
        char_width = 2 if unicodedata.east_asian_width(char) in ('F', 'W') else 1
        if width + char_width > max_width:
            break
        width += char_width
        end_pos = i + 1
    return s[:end_pos]

def hide_cursor():
    """Hides the terminal cursor."""
    print('\033[?25l', end='')

def show_cursor():
    """Shows the terminal cursor."""
    print('\033[?25h', end='')

def move_cursor_up(lines: int):
    """Moves the cursor up by a number of lines."""
    if lines > 0:
        print(f'\033[{lines}A', end='')

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text: str, color: str = Color.CYAN):
    """
    Prints a centered header with separators that fill the terminal width.
    Accounts for CJK character widths.
    
    :param text: The text to display in the header.
    :param color: ANSI color code for the header text.
    """
    width = get_terminal_width()
    padded_text = f" {text} "
    text_display_width = get_display_width(padded_text)
    
    # Handle cases where the text is wider than the terminal
    if text_display_width >= width:
        print(f"\n{Color.BOLD}{color}{text}{Color.RESET}")
        return
        
    separator_total_len = width - text_display_width
    l_separator_len = separator_total_len // 2
    r_separator_len = separator_total_len - l_separator_len
    
    l_separator = "━" * l_separator_len
    r_separator = "━" * r_separator_len
    
    print(f"\n{Color.BOLD}{color}{l_separator}{padded_text}{r_separator}{Color.RESET}")

def print_status(message: str, success: Optional[bool] = None, status: str = 'info', indent: int = 0):
    """
    Prints a status message with a symbol and color.
    
    :param message: The status message to print.
    :param success: (Deprecated) If True, sets status to 'success'; if False, 'error'.
    :param status: 'success', 'error', 'warning', or 'info'.
    :param indent: Number of spaces to indent.
    """
    prefix = "  " * indent
    
    # Backward compatibility
    if success is not None:
        status = 'success' if success else 'error'
        
    if status == 'success':
        symbol = f"{Color.GREEN}✓"
    elif status == 'error':
        symbol = f"{Color.RED}✗"
    elif status == 'warning':
        symbol = f"{Color.YELLOW}⚠"
    else:  # 'info'
        symbol = f"{Color.BLUE}ℹ{Color.RESET}"
        
    print(f"{prefix}[{symbol}] {message}{Color.RESET}")

def wait_key(message: str = ""):
    """
    Prints a message and waits for a single key press from the user.
    This is a cross-platform function.

    :param message: The message to display before waiting.
    """
    print(message, end="", flush=True)

    if os.name == 'nt':
        import msvcrt
        msvcrt.getch()
    else:
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Add a newline after the key is pressed for cleaner output
    print()
