"""
Tkinter GUI application for Sticky Note Organizer
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .database import StickyNotesDatabase
from .categorizer import NoteCategorizer
from .exporters import ExportManager
from .filters import NoteFilter, NoteSorter
from .backup import BackupManager
from .analytics import AdvancedAnalytics
from .editor import NoteEditor


class StickyNoteGUI(tk.Tk):
    """Main GUI application for Sticky Note Organizer"""

    def __init__(self):
        super().__init__()

        self.title("Sticky Note Organizer")
        self.geometry("1200x700")

        # Data storage
        self.db_path = None
        self.notes = []
        self.categorized_notes = {}
        self.filtered_notes = []
        self.selected_note = None

        # Initialize components
        self.db = StickyNotesDatabase()
        self.categorizer = NoteCategorizer()
        self.analytics = AdvancedAnalytics()

        # Setup UI
        self.create_widgets()
        self.auto_connect_database()

    def create_widgets(self):
        """Create all GUI widgets"""

        # Menu bar
        self.create_menu()

        # Database connection frame
        self.create_connection_frame()

        # Main notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.create_browser_tab()
        self.create_filter_tab()
        self.create_stats_tab()
        self.create_backup_tab()
        self.create_settings_tab()

        # Status bar
        self.create_status_bar()

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Database...", command=self.open_database)
        file_menu.add_command(label="Create Backup", command=self.create_backup_cmd)
        file_menu.add_separator()
        file_menu.add_command(label="Export All...", command=self.export_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Refresh", command=self.load_notes)
        tools_menu.add_command(label="Find Duplicates", command=self.find_duplicates)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_connection_frame(self):
        """Create database connection frame"""
        conn_frame = ttk.Frame(self)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(conn_frame, text="Database:").pack(side=tk.LEFT, padx=5)

        self.db_path_var = tk.StringVar(value="Not connected")
        ttk.Label(conn_frame, textvariable=self.db_path_var, relief=tk.SUNKEN, anchor=tk.W).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )

        ttk.Button(conn_frame, text="Connect", command=self.open_database).pack(side=tk.LEFT, padx=5)
        ttk.Button(conn_frame, text="Refresh", command=self.load_notes).pack(side=tk.LEFT)

    def create_browser_tab(self):
        """Create notes browser tab"""
        browser_tab = ttk.Frame(self.notebook)
        self.notebook.add(browser_tab, text="Browser")

        # Create paned window for resizable sections
        paned = ttk.PanedWindow(browser_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Categories
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Categories", font=('Arial', 10, 'bold')).pack(pady=5)

        # Category listbox
        self.category_listbox = tk.Listbox(left_frame, exportselection=False)
        self.category_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)

        # Middle panel - Notes list
        middle_frame = ttk.Frame(paned)
        paned.add(middle_frame, weight=2)

        # Search box
        search_frame = ttk.Frame(middle_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Notes listbox
        notes_list_frame = ttk.Frame(middle_frame)
        notes_list_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        scrollbar = ttk.Scrollbar(notes_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notes_listbox = tk.Listbox(notes_list_frame, yscrollcommand=scrollbar.set)
        self.notes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.notes_listbox.bind('<<ListboxSelect>>', self.on_note_select)
        scrollbar.config(command=self.notes_listbox.yview)

        # Right panel - Note preview/editor
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="Note Content", font=('Arial', 10, 'bold')).pack(pady=5)

        # Note text area
        self.note_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, height=20)
        self.note_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Save Changes", command=self.save_note_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete Note", command=self.delete_note).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Duplicate", command=self.duplicate_note).pack(side=tk.LEFT, padx=2)

        # Export buttons
        export_frame = ttk.LabelFrame(browser_tab, text="Export")
        export_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(export_frame, text="CSV", command=lambda: self.export('csv')).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(export_frame, text="JSON", command=lambda: self.export('json')).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(export_frame, text="Excel", command=lambda: self.export('excel')).pack(side=tk.LEFT, padx=2, pady=2)
        ttk.Button(export_frame, text="Markdown", command=lambda: self.export('markdown')).pack(side=tk.LEFT, padx=2, pady=2)

    def create_filter_tab(self):
        """Create advanced filtering tab"""
        filter_tab = ttk.Frame(self.notebook)
        self.notebook.add(filter_tab, text="Filter")

        # Left panel - Filter controls
        left_frame = ttk.LabelFrame(filter_tab, text="Filter Options")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

        # Date range
        date_frame = ttk.LabelFrame(left_frame, text="Date Range")
        date_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(date_frame, text="From:").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.date_from_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_from_var, width=15).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(date_frame, text="To:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.date_to_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_to_var, width=15).grid(row=1, column=1, padx=2, pady=2)

        # Category filter
        cat_frame = ttk.LabelFrame(left_frame, text="Categories")
        cat_frame.pack(fill=tk.X, padx=5, pady=5)

        self.filter_categories = tk.Listbox(cat_frame, selectmode=tk.MULTIPLE, height=6)
        self.filter_categories.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Content length
        len_frame = ttk.LabelFrame(left_frame, text="Content Length")
        len_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(len_frame, text="Min:").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.min_length_var = tk.StringVar(value="0")
        ttk.Entry(len_frame, textvariable=self.min_length_var, width=10).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(len_frame, text="Max:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.max_length_var = tk.StringVar(value="99999")
        ttk.Entry(len_frame, textvariable=self.max_length_var, width=10).grid(row=1, column=1, padx=2, pady=2)

        # Keywords
        kw_frame = ttk.LabelFrame(left_frame, text="Keywords")
        kw_frame.pack(fill=tk.X, padx=5, pady=5)

        self.keywords_var = tk.StringVar()
        ttk.Entry(kw_frame, textvariable=self.keywords_var).pack(fill=tk.X, padx=2, pady=2)
        ttk.Label(kw_frame, text="(comma-separated)", font=('Arial', 8)).pack()

        # Filter buttons
        ttk.Button(left_frame, text="Apply Filter", command=self.apply_filter).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(left_frame, text="Reset", command=self.reset_filter).pack(fill=tk.X, padx=5, pady=2)

        # Right panel - Filtered results
        right_frame = ttk.LabelFrame(filter_tab, text="Filtered Notes")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.filter_count_var = tk.StringVar(value="0 notes")
        ttk.Label(right_frame, textvariable=self.filter_count_var).pack(pady=2)

        self.filtered_listbox = tk.Listbox(right_frame)
        self.filtered_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(right_frame, text="Export Filtered", command=self.export_filtered).pack(pady=5)

    def create_stats_tab(self):
        """Create statistics dashboard tab"""
        stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(stats_tab, text="Statistics")

        # Top frame - Summary stats
        summary_frame = ttk.LabelFrame(stats_tab, text="Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)

        self.stats_text = tk.Text(summary_frame, height=8, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)

        # Charts frame
        charts_frame = ttk.Frame(stats_tab)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if MATPLOTLIB_AVAILABLE:
            # Category distribution chart
            self.stats_figure = Figure(figsize=(10, 5))
            self.stats_canvas = FigureCanvasTkAgg(self.stats_figure, charts_frame)
            self.stats_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Generate button
        ttk.Button(stats_tab, text="Generate Statistics", command=self.generate_statistics).pack(pady=5)

    def create_backup_tab(self):
        """Create backup/restore tab"""
        backup_tab = ttk.Frame(self.notebook)
        self.notebook.add(backup_tab, text="Backup")

        # Current database info
        info_frame = ttk.LabelFrame(backup_tab, text="Current Database")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.db_info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
        self.db_info_text.pack(fill=tk.X, padx=5, pady=5)

        # Backup controls
        backup_frame = ttk.LabelFrame(backup_tab, text="Create Backup")
        backup_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(backup_frame, text="Create Backup Now", command=self.create_backup_cmd).pack(pady=10)

        # Backup list
        list_frame = ttk.LabelFrame(backup_tab, text="Available Backups")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.backup_listbox = tk.Listbox(list_frame)
        self.backup_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Restore/Delete buttons
        btn_frame = ttk.Frame(backup_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Restore Selected", command=self.restore_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_backups).pack(side=tk.LEFT, padx=2)

    def create_settings_tab(self):
        """Create settings tab"""
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Settings")

        # Custom categories
        cat_frame = ttk.LabelFrame(settings_tab, text="Custom Categories")
        cat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(cat_frame, text="Add custom categories and keywords for auto-categorization").pack(pady=5)

        # Category name
        name_frame = ttk.Frame(cat_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(name_frame, text="Category Name:").pack(side=tk.LEFT, padx=2)
        self.custom_cat_name = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.custom_cat_name).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Keywords
        kw_frame = ttk.Frame(cat_frame)
        kw_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(kw_frame, text="Keywords:").pack(side=tk.LEFT, padx=2)
        self.custom_cat_keywords = tk.StringVar()
        ttk.Entry(kw_frame, textvariable=self.custom_cat_keywords).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        ttk.Button(cat_frame, text="Add Category", command=self.add_custom_category).pack(pady=5)

    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        self.note_count_var = tk.StringVar(value="0 notes")
        ttk.Label(status_frame, textvariable=self.note_count_var).pack(side=tk.RIGHT, padx=5)

    # Database operations
    def auto_connect_database(self):
        """Automatically connect to database"""
        if self.db.connect():
            self.db_path = self.db.db_path
            self.db_path_var.set(self.db_path)
            self.load_notes()
        else:
            self.status_var.set("No database found - please connect manually")

    def open_database(self):
        """Open database file dialog"""
        filename = filedialog.askopenfilename(
            title="Select Sticky Notes Database",
            filetypes=[("SQLite Database", "*.sqlite"), ("All Files", "*.*")]
        )

        if filename:
            self.db.close()
            if self.db.connect(filename):
                self.db_path = filename
                self.db_path_var.set(filename)
                self.load_notes()
            else:
                messagebox.showerror("Error", "Failed to connect to database")

    def load_notes(self):
        """Load notes from database"""
        if not self.db.connection:
            messagebox.showwarning("Warning", "Not connected to database")
            return

        try:
            self.notes = self.db.extract_notes()
            self.categorized_notes = self.categorizer.categorize_notes(self.notes)

            # Update UI
            self.update_category_list()
            self.update_filter_categories()
            self.note_count_var.set(f"{len(self.notes)} notes")
            self.status_var.set(f"Loaded {len(self.notes)} notes")

            # Update database info
            self.update_db_info()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {e}")

    def update_category_list(self):
        """Update category listbox"""
        self.category_listbox.delete(0, tk.END)
        self.category_listbox.insert(tk.END, "All Notes")

        for category, notes in sorted(self.categorized_notes.items()):
            self.category_listbox.insert(tk.END, f"{category} ({len(notes)})")

    def update_filter_categories(self):
        """Update filter categories listbox"""
        self.filter_categories.delete(0, tk.END)

        for category in sorted(self.categorized_notes.keys()):
            self.filter_categories.insert(tk.END, category)

    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.category_listbox.curselection()

        if not selection:
            return

        index = selection[0]

        if index == 0:  # All Notes
            notes_to_show = self.notes
        else:
            category = list(sorted(self.categorized_notes.keys()))[index - 1]
            notes_to_show = self.categorized_notes[category]

        # Update notes list
        self.notes_listbox.delete(0, tk.END)

        for note in notes_to_show:
            preview = note['content'][:50].replace('\n', ' ')
            self.notes_listbox.insert(tk.END, preview)

        self.filtered_notes = notes_to_show

    def on_note_select(self, event):
        """Handle note selection"""
        selection = self.notes_listbox.curselection()

        if not selection or not self.filtered_notes:
            return

        index = selection[0]
        self.selected_note = self.filtered_notes[index]

        # Display note content
        self.note_text.delete('1.0', tk.END)
        self.note_text.insert('1.0', self.selected_note['content'])

    def on_search_change(self, *args):
        """Handle search box changes"""
        search_term = self.search_var.get().lower()

        if not search_term:
            self.on_category_select(None)
            return

        # Filter notes by search term
        matching_notes = [n for n in self.filtered_notes if search_term in n['content'].lower()]

        self.notes_listbox.delete(0, tk.END)

        for note in matching_notes:
            preview = note['content'][:50].replace('\n', ' ')
            self.notes_listbox.insert(tk.END, preview)

    # Note operations
    def save_note_changes(self):
        """Save changes to selected note"""
        if not self.selected_note:
            messagebox.showwarning("Warning", "No note selected")
            return

        new_content = self.note_text.get('1.0', tk.END).strip()

        try:
            with NoteEditor(self.db_path) as editor:
                success = editor.update_note(self.selected_note['id'], new_content)

                if success:
                    messagebox.showinfo("Success", "Note updated successfully")
                    self.load_notes()
                else:
                    messagebox.showerror("Error", "Failed to update note")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save note: {e}")

    def delete_note(self):
        """Delete selected note"""
        if not self.selected_note:
            messagebox.showwarning("Warning", "No note selected")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this note?")

        if confirm:
            try:
                with NoteEditor(self.db_path) as editor:
                    success = editor.delete_note(self.selected_note['id'], permanent=True)

                    if success:
                        messagebox.showinfo("Success", "Note deleted")
                        self.load_notes()
                    else:
                        messagebox.showerror("Error", "Failed to delete note")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete note: {e}")

    def duplicate_note(self):
        """Duplicate selected note"""
        if not self.selected_note:
            messagebox.showwarning("Warning", "No note selected")
            return

        try:
            with NoteEditor(self.db_path) as editor:
                new_id = editor.duplicate_note(self.selected_note['id'])

                if new_id:
                    messagebox.showinfo("Success", "Note duplicated")
                    self.load_notes()
                else:
                    messagebox.showerror("Error", "Failed to duplicate note")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to duplicate note: {e}")

    # Filter operations
    def apply_filter(self):
        """Apply advanced filters"""
        if not self.notes:
            messagebox.showwarning("Warning", "No notes loaded")
            return

        filter_engine = NoteFilter()

        # Apply date range
        date_from = self.date_from_var.get()
        date_to = self.date_to_var.get()

        if date_from and date_to:
            filter_engine.by_date_range(date_from, date_to)

        # Apply category filter
        selected_cats = [self.filter_categories.get(i) for i in self.filter_categories.curselection()]

        if selected_cats:
            filter_engine.by_category(selected_cats)

        # Apply content length filter
        try:
            min_len = int(self.min_length_var.get())
            max_len = int(self.max_length_var.get())
            filter_engine.by_content_length(min_len, max_len)
        except ValueError:
            pass

        # Apply keywords
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]

        if keywords:
            filter_engine.by_keywords(keywords, match_all=False)

        # Apply filter
        self.filtered_notes = filter_engine.apply(self.notes)

        # Update UI
        self.filtered_listbox.delete(0, tk.END)

        for note in self.filtered_notes:
            preview = note['content'][:50].replace('\n', ' ')
            self.filtered_listbox.insert(tk.END, preview)

        self.filter_count_var.set(f"{len(self.filtered_notes)} notes")

    def reset_filter(self):
        """Reset all filters"""
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.filter_categories.selection_clear(0, tk.END)
        self.min_length_var.set("0")
        self.max_length_var.set("99999")
        self.keywords_var.set("")
        self.filtered_listbox.delete(0, tk.END)
        self.filter_count_var.set("0 notes")

    def export_filtered(self):
        """Export filtered notes"""
        if not self.filtered_notes:
            messagebox.showwarning("Warning", "No filtered notes to export")
            return

        self.export_notes(self.filtered_notes, "filtered_notes")

    # Statistics operations
    def generate_statistics(self):
        """Generate and display statistics"""
        if not self.notes:
            messagebox.showwarning("Warning", "No notes loaded")
            return

        # Get statistics
        stats = self.analytics.get_category_stats(self.categorized_notes)
        word_freq = self.analytics.get_word_frequency(self.notes, top_n=10)

        # Display summary
        self.stats_text.delete('1.0', tk.END)

        summary = f"Total Notes: {len(self.notes)}\n"
        summary += f"Categories: {len(self.categorized_notes)}\n\n"
        summary += "Top Categories:\n"

        for cat, stat in sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
            summary += f"  {cat}: {stat['count']} ({stat['percentage']:.1f}%)\n"

        summary += "\nTop Keywords:\n"

        for word, count in word_freq:
            summary += f"  {word}: {count}\n"

        self.stats_text.insert('1.0', summary)

        # Create chart
        if MATPLOTLIB_AVAILABLE and stats:
            self.stats_figure.clear()

            # Category distribution pie chart
            ax = self.stats_figure.add_subplot(111)

            categories = list(stats.keys())[:10]  # Top 10
            counts = [stats[c]['count'] for c in categories]

            ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax.set_title("Category Distribution")

            self.stats_canvas.draw()

    # Backup operations
    def create_backup_cmd(self):
        """Create backup"""
        if not self.db_path:
            messagebox.showwarning("Warning", "No database connected")
            return

        try:
            backup_mgr = BackupManager()
            backup_file = backup_mgr.create_backup(self.db_path, compress=True)

            messagebox.showinfo("Success", f"Backup created:\n{backup_file}")
            self.refresh_backups()

        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {e}")

    def restore_backup(self):
        """Restore from selected backup"""
        selection = self.backup_listbox.curselection()

        if not selection:
            messagebox.showwarning("Warning", "No backup selected")
            return

        confirm = messagebox.askyesno("Confirm", "Restore from this backup?\nCurrent database will be backed up first.")

        if confirm:
            # Implementation would go here
            messagebox.showinfo("Info", "Restore functionality - implementation in progress")

    def delete_backup(self):
        """Delete selected backup"""
        selection = self.backup_listbox.curselection()

        if not selection:
            messagebox.showwarning("Warning", "No backup selected")
            return

        confirm = messagebox.askyesno("Confirm", "Delete this backup?")

        if confirm:
            # Implementation would go here
            messagebox.showinfo("Info", "Delete functionality - implementation in progress")

    def refresh_backups(self):
        """Refresh backup list"""
        self.backup_listbox.delete(0, tk.END)

        try:
            backup_mgr = BackupManager()
            backups = backup_mgr.list_backups()

            for backup in backups:
                size_str = BackupManager.format_size(backup['size'])
                date_str = backup['created'].strftime('%Y-%m-%d %H:%M')
                self.backup_listbox.insert(tk.END, f"{backup['name']} - {date_str} ({size_str})")

        except Exception as e:
            self.status_var.set(f"Failed to list backups: {e}")

    def update_db_info(self):
        """Update database info display"""
        if not self.db_path:
            return

        info = f"Path: {self.db_path}\n"

        if os.path.exists(self.db_path):
            size = os.path.getsize(self.db_path)
            info += f"Size: {BackupManager.format_size(size)}\n"
            mtime = datetime.fromtimestamp(os.path.getmtime(self.db_path))
            info += f"Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n"

        self.db_info_text.delete('1.0', tk.END)
        self.db_info_text.insert('1.0', info)

    # Settings operations
    def add_custom_category(self):
        """Add custom category"""
        name = self.custom_cat_name.get().strip()
        keywords_str = self.custom_cat_keywords.get().strip()

        if not name or not keywords_str:
            messagebox.showwarning("Warning", "Please enter both name and keywords")
            return

        keywords = [k.strip() for k in keywords_str.split(',')]

        self.categorizer.add_custom_category(name, keywords)

        messagebox.showinfo("Success", f"Added category: {name}")

        # Clear inputs
        self.custom_cat_name.set("")
        self.custom_cat_keywords.set("")

    # Export operations
    def export(self, format_type):
        """Export notes in specified format"""
        self.export_notes(self.notes, "sticky_notes", [format_type])

    def export_all(self):
        """Export all notes in multiple formats"""
        formats = ['csv', 'json', 'excel', 'markdown']
        self.export_notes(self.notes, "sticky_notes", formats)

    def export_notes(self, notes, filename, formats=None):
        """Export notes to file"""
        if not notes:
            messagebox.showwarning("Warning", "No notes to export")
            return

        if formats is None:
            formats = ['csv']

        try:
            export_mgr = ExportManager("exports")
            results = export_mgr.export(notes, formats, filename)

            success_msg = "Export successful:\n"

            for fmt, path in results.items():
                if "Error" not in path:
                    success_msg += f"\n{fmt}: {path}"

            messagebox.showinfo("Success", success_msg)

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def find_duplicates(self):
        """Find duplicate notes"""
        if not self.notes:
            messagebox.showwarning("Warning", "No notes loaded")
            return

        similar = self.analytics.find_similar_notes(self.notes, threshold=0.8)

        if not similar:
            messagebox.showinfo("Info", "No duplicates found")
        else:
            msg = f"Found {len(similar)} potential duplicates:\n\n"

            for note1, note2, sim in similar[:5]:
                preview1 = note1['content'][:30]
                preview2 = note2['content'][:30]
                msg += f"- {preview1}... ↔ {preview2}... ({sim:.0%} similar)\n"

            messagebox.showinfo("Duplicates Found", msg)

    def show_about(self):
        """Show about dialog"""
        about_text = """Sticky Note Organizer v1.0.0

A powerful tool to extract, organize, and analyze
Microsoft Sticky Notes.

Features:
• Automatic categorization
• Advanced filtering
• Statistics dashboard
• Backup/restore
• Multiple export formats

Created with Python and Tkinter"""

        messagebox.showinfo("About", about_text)


def main():
    """Launch the GUI application"""
    app = StickyNoteGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
