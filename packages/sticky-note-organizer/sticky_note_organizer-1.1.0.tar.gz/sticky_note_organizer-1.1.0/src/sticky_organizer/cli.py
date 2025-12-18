"""
Command-line interface for Sticky Note Organizer
"""

import click
import os
from pathlib import Path
from typing import List, Optional

try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama for Windows
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

from .database import StickyNotesDatabase
from .categorizer import NoteCategorizer
from .exporters import ExportManager
from .backup import BackupManager
from .editor import NoteEditor


def print_colored(message: str, color: str = "white"):
    """Print colored message if colorama is available"""
    # Robust handling of problematic characters for Windows console
    import sys

    # Get the console encoding, fallback to utf-8
    encoding = sys.stdout.encoding or 'utf-8'

    # Clean message for console output
    try:
        # Try to encode with the console encoding
        message.encode(encoding)
    except (UnicodeEncodeError, AttributeError):
        # If that fails, use ASCII with replacement
        message = message.encode('ascii', errors='replace').decode('ascii')

    # Replace common problematic characters
    message = message.replace('\x00', '')  # Remove null bytes

    if not COLORS_AVAILABLE:
        try:
            print(message, flush=True)
        except (OSError, UnicodeEncodeError):
            # Last resort: strip to ASCII
            print(message.encode('ascii', errors='ignore').decode('ascii'), flush=True)
        return

    color_map = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
    }

    try:
        output = f"{color_map.get(color, Fore.WHITE)}{message}{Style.RESET_ALL}"
        print(output, flush=True)
    except (UnicodeEncodeError, OSError):
        # Fallback to plain print without colors
        try:
            print(message, flush=True)
        except (OSError, UnicodeEncodeError):
            # Last resort
            print(message.encode('ascii', errors='ignore').decode('ascii'), flush=True)


def print_stats(categorized_notes, total_notes):
    """Print statistics about the notes"""
    print_colored("\n📊 EXTRACTION SUMMARY", "cyan")
    print_colored("=" * 50, "blue")
    print_colored(f"Total notes extracted: {total_notes}", "green")
    print_colored(f"Categories found: {len(categorized_notes)}", "green")
    
    print_colored("\n📂 CATEGORY BREAKDOWN:", "yellow")
    sorted_categories = sorted(categorized_notes.items(), key=lambda x: len(x[1]), reverse=True)
    
    for category, notes in sorted_categories:
        count = len(notes)
        percentage = (count / total_notes * 100) if total_notes > 0 else 0
        print_colored(f"  {category:<25} {count:>3} notes ({percentage:>5.1f}%)", "white")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Sticky Note Organizer

    A powerful CLI tool to extract, organize, and analyze Microsoft Sticky Notes.
    Automatically finds your sticky notes database and organizes them by themes.
    """
    pass


@cli.command()
@click.option('--db-path', '-d', help='Path to sticky notes database file')
@click.option('--output-dir', '-o', default='output', help='Output directory for exported files')
@click.option('--formats', '-f', multiple=True, default=['csv', 'summary'], 
              help='Export formats (csv, json, excel, markdown, summary)')
@click.option('--filename', default='sticky_notes', help='Base filename for exported files')
@click.option('--show-stats/--no-stats', default=True, help='Show extraction statistics')
def extract(db_path, output_dir, formats, filename, show_stats):
    """Extract and organize sticky notes from the database"""
    
    print_colored("🔍 Starting Sticky Notes extraction...", "cyan")
    
    # Initialize database
    db = StickyNotesDatabase()
    
    if not db.connect(db_path):
        print_colored("❌ Could not find or connect to sticky notes database!", "red")
        print_colored("💡 Make sure Microsoft Sticky Notes is installed and has been used.", "yellow")
        return
    
    print_colored(f"✅ Connected to database: {db.db_path}", "green")
    
    # Extract notes
    notes = db.extract_notes()
    db.close()
    
    if not notes:
        print_colored("⚠️  No notes found in the database.", "yellow")
        return
    
    print_colored(f"📝 Extracted {len(notes)} notes", "green")
    
    # Categorize notes
    categorizer = NoteCategorizer()
    categorized_notes = categorizer.categorize_notes(notes)
    
    # Add category to each note for export
    all_notes_with_categories = []
    for category, category_notes in categorized_notes.items():
        all_notes_with_categories.extend(category_notes)
    
    # Export files
    export_manager = ExportManager(output_dir)
    available_formats = export_manager.get_available_formats()
    
    # Filter requested formats to available ones
    valid_formats = [f for f in formats if f in available_formats]
    invalid_formats = [f for f in formats if f not in available_formats]
    
    if invalid_formats:
        print_colored(f"⚠️  Skipping unavailable formats: {', '.join(invalid_formats)}", "yellow")
    
    if valid_formats:
        # Separate summary format from other formats (summary needs categorized notes)
        regular_formats = [f for f in valid_formats if f != 'summary']
        has_summary = 'summary' in valid_formats

        if regular_formats:
            print_colored(f"📤 Exporting to formats: {', '.join(regular_formats)}", "blue")

            results = export_manager.export(all_notes_with_categories, regular_formats, filename)

            print_colored("\n📁 EXPORTED FILES:", "green")
            for fmt, filepath in results.items():
                if "Error" in filepath:
                    print_colored(f"  ❌ {fmt}: {filepath}", "red")
                else:
                    print_colored(f"  ✅ {fmt}: {filepath}", "green")

        # Export summary if requested
        if has_summary:
            try:
                summary_path = export_manager.export_summary(categorized_notes, f"{filename}_summary")
                print_colored(f"  ✅ Summary: {summary_path}", "green")
            except Exception as e:
                print_colored(f"  ⚠  Summary export warning: {e}", "yellow")
    
    # Show statistics
    if show_stats:
        print_stats(categorized_notes, len(notes))
    
    print_colored(f"\n🎉 Extraction completed! Check the '{output_dir}' directory for your files.", "cyan")


@cli.command()
@click.option('--db-path', '-d', help='Path to sticky notes database file')
def info(db_path):
    """Show information about the sticky notes database"""
    
    print_colored("🔍 Analyzing sticky notes database...", "cyan")
    
    db = StickyNotesDatabase()
    
    if not db.connect(db_path):
        print_colored("❌ Could not find or connect to sticky notes database!", "red")
        
        # Show possible locations
        print_colored("\n💡 Checked these locations:", "yellow")
        system_paths = [
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Packages', 
                        'Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe', 'LocalState', 'plum.sqlite'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Roaming', 'Microsoft', 
                        'Sticky Notes', 'StickyNotes.snt'),
            './plum.sqlite'
        ]
        
        for path in system_paths:
            exists = "✅" if os.path.exists(path) else "❌"
            print_colored(f"  {exists} {path}", "white")
        return
    
    print_colored(f"✅ Connected to: {db.db_path}", "green")
    
    # Get database info
    tables = db.get_table_info()
    notes = db.extract_notes()
    
    print_colored(f"\n📊 DATABASE INFORMATION:", "cyan")
    print_colored(f"  Database file: {db.db_path}", "white")
    print_colored(f"  File size: {os.path.getsize(db.db_path):,} bytes", "white")
    print_colored(f"  Total tables: {len(tables)}", "white")
    print_colored(f"  Total notes: {len(notes)}", "white")
    
    if tables:
        print_colored(f"\n📋 TABLES FOUND:", "yellow")
        for table, columns in tables.items():
            print_colored(f"  {table}: {len(columns)} columns", "white")
    
    if notes:
        # Show date range
        dates = [note['created_date'] for note in notes if note['created_date'] != 'Unknown']
        if dates:
            print_colored(f"\n📅 DATE RANGE:", "yellow")
            print_colored(f"  Oldest note: {min(dates)}", "white")
            print_colored(f"  Newest note: {max(dates)}", "white")
        
        # Show themes
        themes = {}
        for note in notes:
            theme = note.get('theme', 'Unknown')
            themes[theme] = themes.get(theme, 0) + 1
        
        if len(themes) > 1:
            print_colored(f"\n🎨 THEMES USED:", "yellow")
            for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True):
                print_colored(f"  {theme}: {count} notes", "white")
    
    db.close()


@cli.command()
def categories():
    """Show available note categories and their keywords"""
    
    categorizer = NoteCategorizer()
    all_categories = categorizer.get_categories()
    
    print_colored("📂 AVAILABLE CATEGORIES", "cyan")
    print_colored("=" * 50, "blue")
    
    for category, keywords in all_categories.items():
        print_colored(f"\n{category} ({len(keywords)} keywords):", "yellow")
        
        # Show first 10 keywords, then "and X more..."
        display_keywords = keywords[:10]
        remaining = len(keywords) - 10
        
        keyword_text = ", ".join(display_keywords)
        if remaining > 0:
            keyword_text += f" and {remaining} more..."
        
        print_colored(f"  {keyword_text}", "white")


@cli.command()
@click.argument('search_term')
@click.option('--db-path', '-d', help='Path to sticky notes database file')
@click.option('--category', '-c', help='Filter by category')
@click.option('--case-sensitive', is_flag=True, help='Case-sensitive search')
def search(search_term, db_path, category, case_sensitive):
    """Search for notes containing specific text"""
    
    print_colored(f"🔍 Searching for: '{search_term}'", "cyan")
    
    # Extract notes
    db = StickyNotesDatabase()
    if not db.connect(db_path):
        print_colored("❌ Could not connect to database!", "red")
        return
    
    notes = db.extract_notes()
    db.close()
    
    if not notes:
        print_colored("No notes found in database.", "yellow")
        return
    
    # Categorize if category filter is specified
    if category:
        categorizer = NoteCategorizer()
        categorized_notes = categorizer.categorize_notes(notes)
        
        if category not in categorized_notes:
            print_colored(f"Category '{category}' not found!", "red")
            return
        
        notes = categorized_notes[category]
    
    # Search
    search_func = (lambda x: search_term in x) if case_sensitive else (lambda x: search_term.lower() in x.lower())
    
    matching_notes = [note for note in notes if search_func(note['content'])]
    
    if not matching_notes:
        category_text = f" in category '{category}'" if category else ""
        print_colored(f"No notes found containing '{search_term}'{category_text}", "yellow")
        return
    
    print_colored(f"\n✅ Found {len(matching_notes)} matching notes:", "green")
    
    for i, note in enumerate(matching_notes, 1):
        print_colored(f"\n--- Note {i} ---", "blue")
        print_colored(f"Date: {note['created_date']}", "yellow")
        if note.get('category'):
            print_colored(f"Category: {note['category']}", "yellow")
        print_colored(f"Content: {note['content'][:200]}{'...' if len(note['content']) > 200 else ''}", "white")


@cli.command()
@click.option('--db-path', '-d', help='Path to sticky notes database file')
@click.option('--output-dir', '-o', default='backups', help='Backup directory')
@click.option('--compress/--no-compress', default=True, help='Compress backup as ZIP')
def backup(db_path, output_dir, compress):
    """Create a backup of the sticky notes database"""

    print_colored(" Creating backup...", "cyan")

    # Get database path
    if not db_path:
        db = StickyNotesDatabase()
        if not db.connect():
            print_colored(" Could not find database!", "red")
            return
        db_path = db.db_path
        db.close()

    # Create backup
    backup_mgr = BackupManager(output_dir)

    try:
        backup_file = backup_mgr.create_backup(db_path, compress=compress)
        file_size = BackupManager.format_size(Path(backup_file).stat().st_size)

        print_colored(f" Backup created successfully!", "green")
        print_colored(f"  File: {backup_file}", "white")
        print_colored(f"  Size: {file_size}", "white")

    except Exception as e:
        print_colored(f" Backup failed: {e}", "red")


@cli.command()
@click.argument('backup_file')
@click.option('--db-path', '-d', help='Target database path (default: auto-detect)')
@click.option('--no-backup', is_flag=True, help='Skip backing up current database')
def restore(backup_file, db_path, no_backup):
    """Restore database from a backup file"""

    print_colored(" Restoring from backup...", "cyan")

    # Get target database path
    if not db_path:
        db = StickyNotesDatabase()
        if not db.connect():
            print_colored(" Could not find database location!", "red")
            return
        db_path = db.db_path
        db.close()

    # Confirm restoration
    print_colored(f"  Source: {backup_file}", "yellow")
    print_colored(f"  Target: {db_path}", "yellow")

    if not no_backup:
        print_colored("\n  A backup of the current database will be created first.", "white")

    confirm = input("\nProceed with restoration? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print_colored(" Restoration cancelled.", "yellow")
        return

    # Restore backup
    backup_mgr = BackupManager()

    try:
        backup_mgr.restore_backup(backup_file, db_path, create_backup_first=not no_backup)
        print_colored(" Database restored successfully!", "green")

    except Exception as e:
        print_colored(f" Restoration failed: {e}", "red")


@cli.command()
@click.argument('note_id')
@click.argument('new_content')
@click.option('--db-path', '-d', help='Path to sticky notes database file')
def edit(note_id, new_content, db_path):
    """Edit the content of a note by ID"""

    print_colored(" Editing note...", "cyan")

    # Get database path
    if not db_path:
        db = StickyNotesDatabase()
        if not db.connect():
            print_colored(" Could not find database!", "red")
            return
        db_path = db.db_path
        db.close()

    # Edit note
    try:
        with NoteEditor(db_path) as editor:
            success = editor.update_note(note_id, new_content)

            if success:
                print_colored(" Note updated successfully!", "green")
            else:
                print_colored(" Note not found or update failed.", "yellow")

    except Exception as e:
        print_colored(f" Edit failed: {e}", "red")


@cli.command()
@click.argument('note_ids', nargs=-1, required=True)
@click.option('--db-path', '-d', help='Path to sticky notes database file')
@click.option('--separator', '-s', default='\n\n---\n\n', help='Separator between merged notes')
def merge(note_ids, db_path, separator):
    """Merge multiple notes into one"""

    if len(note_ids) < 2:
        print_colored(" Need at least 2 note IDs to merge!", "red")
        return

    print_colored(f" Merging {len(note_ids)} notes...", "cyan")

    # Get database path
    if not db_path:
        db = StickyNotesDatabase()
        if not db.connect():
            print_colored(" Could not find database!", "red")
            return
        db_path = db.db_path
        db.close()

    # Merge notes
    try:
        with NoteEditor(db_path) as editor:
            merged_id = editor.merge_notes(list(note_ids), separator=separator)

            if merged_id:
                print_colored(" Notes merged successfully!", "green")
                print_colored(f"  Merged note ID: {merged_id}", "white")
            else:
                print_colored(" Merge failed.", "yellow")

    except Exception as e:
        print_colored(f" Merge failed: {e}", "red")


@cli.command()
def gui():
    """Launch the GUI application"""

    print_colored(" Launching GUI...", "cyan")

    try:
        from .gui import StickyNoteGUI
        app = StickyNoteGUI()
        app.mainloop()

    except ImportError as e:
        print_colored(" GUI dependencies not installed!", "red")
        print_colored("  Install with: pip install matplotlib Pillow wordcloud", "yellow")

    except Exception as e:
        print_colored(f" Failed to launch GUI: {e}", "red")


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main()