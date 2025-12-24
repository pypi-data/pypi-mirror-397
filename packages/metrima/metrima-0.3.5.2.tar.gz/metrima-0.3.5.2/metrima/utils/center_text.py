"""
Text centering utility for terminal output.

This module provides a function to center text within the terminal
window, with fallback behavior for non-terminal environments.
"""

import os

def center_text(text):
    """
    Center text within the terminal window.
    
    Splits text into lines, finds the longest line, and centers all
    non-empty lines within the terminal width. Falls back to 80 columns
    if terminal size cannot be determined.
    
    :param text: The text to center.
    :type text: str
    :return: Centered text with appropriate padding.
    :rtype: str
    """
    try:
        total_width = os.get_terminal_size().columns
    except OSError:
        total_width = 80

    lines = text.splitlines()

    non_empty_lines = [line.rstrip() for line in lines if line.strip()]

    if not non_empty_lines:
        return ""

    max_length = max(len(line) for line in non_empty_lines)

    left_padding = max(0, (total_width - max_length) // 2)

    centered_lines = []

    for line in non_empty_lines:
        centered_line = ' ' * left_padding + line
        centered_lines.append(centered_line)

    return "\n".join(centered_lines)