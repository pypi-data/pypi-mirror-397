#!/usr/bin/env python3
"""
GUI launcher for Sticky Note Organizer
"""

from .gui import StickyNoteGUI


def main():
    """Launch the GUI application"""
    app = StickyNoteGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
