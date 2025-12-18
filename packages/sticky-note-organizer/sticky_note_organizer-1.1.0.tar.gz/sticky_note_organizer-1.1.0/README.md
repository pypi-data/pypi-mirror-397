# 📝 Sticky Note Organizer

<div align="center">

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

**A powerful Windows application to extract, organize, and analyze Microsoft Sticky Notes with both CLI and GUI interfaces.**

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## 🌟 Overview

Sticky Note Organizer is a comprehensive tool designed to help you manage your Microsoft Sticky Notes more effectively. It automatically detects your sticky notes database, intelligently categorizes notes by themes, and provides both a user-friendly GUI and powerful CLI for maximum flexibility.

Perfect for:
- 📊 **Analyzing** your note-taking patterns
- 🗂️ **Organizing** hundreds of notes automatically
- 💾 **Backing up** your important notes
- 📤 **Exporting** notes to multiple formats (CSV, JSON, Excel, Markdown)
- 🔍 **Searching** and filtering notes efficiently
- 📈 **Visualizing** statistics and insights

## ✨ Features

### Core Capabilities

- **🎯 Auto-Detection**: Automatically finds your Microsoft Sticky Notes database
- **🤖 Smart Categorization**: Organizes notes into 12+ intelligent categories
  - Business Ideas, Financial/Money, Technology/Development
  - Work/Career, Personal Goals, Tasks/Reminders
  - Contacts/People, Travel/Places, Shopping, and more!
- **📦 Multiple Export Formats**: CSV, JSON, Excel, Markdown, and summary reports
- **🔍 Advanced Search & Filtering**: Search by content, category, date range, keywords, and more
- **📊 Analytics Dashboard**: Get insights into your note-taking patterns with interactive charts
- **🎨 Theme Support**: Filter by sticky note colors/themes
- **🪟 Windows Native**: Designed specifically for Windows 10/11 Microsoft Sticky Notes

### GUI Features

<div align="center">

**🖥️ Beautiful, Intuitive Interface**

</div>

- **User-Friendly Interface**: Easy-to-use Tkinter-based GUI for non-technical users
- **Visual Note Browser**: Browse notes by category with live search
- **Advanced Filtering**: Interactive filtering with real-time preview
- **Statistics Dashboard**: Visual charts showing category distribution and trends
- **Note Management**: Edit, delete, merge, and duplicate notes directly in the GUI
- **Backup & Restore**: Create and manage database backups with one click
- **Export Manager**: Export notes in multiple formats with visual feedback

### Advanced Features

- **💾 Backup/Restore**: Automated backup creation with ZIP compression
- **✏️ Note Editing**: Edit note content, merge multiple notes, delete notes
- **🔄 Duplicate Detection**: Find similar notes automatically
- **📝 Word Frequency Analysis**: Discover common keywords in your notes
- **📅 Timeline Analysis**: See when notes were created over time
- **🎨 Custom Categories**: Add your own categories and keywords

## 🚀 Quick Start

### Installation

**Option 1: Quick Install (Recommended)**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Primus-Izzy/Sticky-Note-Organizer.git
   cd Sticky-Note-Organizer
   ```

2. **Run the installer:**
   ```bash
   python install.py
   ```

3. **Verify installation:**
   ```bash
   sticky-organizer --help
   ```

**Option 2: Manual Install**

```bash
pip install -r requirements.txt
pip install -e .
```

### 🎮 Launch the GUI (Super Easy!)

**For Non-Technical Users (Easiest Method):**

Simply **double-click one of these files** in the project folder:

1. **`StickyNoteOrganizer.pyw`** ⭐ **Recommended** (runs without console window)
2. **`launch_gui.bat`** (shows console window for debugging)
3. **`launch_gui.py`** (if you have Python set to open .py files)

That's it! The GUI will open automatically and detect your sticky notes.

**For Command Line Users:**

```bash
# Launch GUI using installed command
sticky-organizer-gui

# Or via CLI
sticky-organizer gui

# Or directly
python -m sticky_organizer.gui_launcher
```

### 💻 CLI Basic Usage

```bash
# Check your database
sticky-organizer info

# Extract and organize your notes
sticky-organizer extract

# Search for specific content
sticky-organizer search "business idea"

# Create a backup
sticky-organizer backup

# View all categories
sticky-organizer categories
```

## 📖 Documentation

### GUI User Guide

The GUI features a tabbed interface with five main sections:

#### 1️⃣ Browser Tab
- **Categories Panel**: View notes organized by category
- **Notes List**: Searchable list of notes in the selected category
- **Note Editor**: View and edit note content
- **Export Options**: Export to CSV, JSON, Excel, or Markdown

**How to use:**
1. Select a category from the left panel
2. Click on a note to view its content
3. Edit the note in the text area
4. Click "Save Changes" to update
5. Use export buttons to save notes to files

#### 2️⃣ Filter Tab
- **Date Range**: Filter notes by creation date
- **Categories**: Select multiple categories to include
- **Content Length**: Filter by minimum/maximum note length
- **Keywords**: Search for specific keywords
- **Live Preview**: See filtered results in real-time

#### 3️⃣ Statistics Tab
- **Summary Statistics**: Total notes, categories, top keywords
- **Category Distribution**: Pie chart showing note distribution
- **Word Frequency**: Most common words in your notes
- **Timeline Chart**: Notes created over time

#### 4️⃣ Backup Tab
- **Database Info**: Current database location and size
- **Create Backup**: One-click backup creation
- **Backup List**: View all available backups
- **Restore**: Restore from a previous backup

#### 5️⃣ Settings Tab
- **Custom Categories**: Add your own categories
- **Keywords**: Define keywords for auto-categorization
- **Export Preferences**: Configure default export settings

### CLI Commands Reference

#### `extract` - Extract and organize notes

```bash
# Basic extraction
sticky-organizer extract

# Custom output directory and formats
sticky-organizer extract -o my_notes -f csv json excel

# Specify database path
sticky-organizer extract -d "C:\path\to\plum.sqlite"
```

**Options:**
- `-d, --db-path`: Path to sticky notes database file
- `-o, --output-dir`: Output directory (default: 'output')
- `-f, --formats`: Export formats (csv, json, excel, markdown, summary)
- `--filename`: Base filename for exported files
- `--show-stats/--no-stats`: Show/hide extraction statistics

#### `search` - Search notes

```bash
# Basic search
sticky-organizer search "project deadline"

# Search within a specific category
sticky-organizer search "meeting" -c "Work/Career"

# Case-sensitive search
sticky-organizer search "API" --case-sensitive
```

#### `backup` - Create database backup

```bash
# Create compressed backup
sticky-organizer backup

# Specify output directory
sticky-organizer backup -o my_backups

# Uncompressed backup
sticky-organizer backup --no-compress
```

#### `restore` - Restore from backup

```bash
# Restore from backup (with safety backup of current database)
sticky-organizer restore backups/sticky_notes_backup_20231215.zip

# Restore without creating safety backup
sticky-organizer restore backup.zip --no-backup
```

#### `edit` - Edit a note

```bash
sticky-organizer edit [note-id] "New content"
```

#### `merge` - Merge multiple notes

```bash
sticky-organizer merge [note-id-1] [note-id-2] [note-id-3]
```

**Options:**
- `-s, --separator`: Text to insert between merged notes

#### `info` - Database information

```bash
sticky-organizer info
```

Shows database location, size, table structure, and note statistics.

#### `categories` - Show available categories

```bash
sticky-organizer categories
```

Displays all categories and their associated keywords.

## 🗂️ Categories

The tool automatically categorizes your notes into these themes:

| Category | Keywords |
|----------|----------|
| **Business Ideas** | Startup, marketing, business, revenue, product, customer |
| **Financial/Money** | Money, payment, salary, budget, investment, cost |
| **Technology/Development** | Code, API, website, software, app, programming |
| **Work/Career** | Work, job, meeting, project, deadline, career |
| **Personal Goals** | Goal, aspiration, dream, improvement, habit |
| **Health/Fitness** | Health, fitness, exercise, workout, diet, medical |
| **Contacts/People** | Phone, email, address, contact |
| **Travel/Places** | Travel, trip, vacation, destination, hotel |
| **Shopping/Items** | Buy, purchase, shopping, store, price |
| **Ideas/Thoughts** | Idea, thought, concept, brainstorm |
| **Tasks/Reminders** | Todo, task, reminder, deadline, appointment |
| **Education/Learning** | Learn, study, course, education, training |

## 📦 Output Files

The tool generates several types of output files:

- **CSV Files** (`.csv`) - All notes with categories and metadata
- **JSON Export** (`.json`) - Machine-readable format with full metadata
- **Excel Workbook** (`.xlsx`) - Multi-sheet workbook organized by category
- **Markdown Report** (`.md`) - Human-readable format for documentation
- **Summary Report** (`.txt`) - Organized overview with key highlights

## 🔧 Advanced Usage

### Using the Python API

```python
from sticky_organizer.database import StickyNotesDatabase
from sticky_organizer.categorizer import NoteCategorizer
from sticky_organizer.exporters import ExportManager
from sticky_organizer.filters import NoteFilter, NoteSorter
from sticky_organizer.backup import BackupManager
from sticky_organizer.analytics import AdvancedAnalytics

# Connect to database
db = StickyNotesDatabase()
if db.connect():
    notes = db.extract_notes()
    db.close()

# Categorize notes
categorizer = NoteCategorizer()
categorized = categorizer.categorize_notes(notes)

# Advanced filtering
filter_engine = NoteFilter()
filtered_notes = (filter_engine
    .by_date_range('2023-01-01', '2023-12-31')
    .by_keywords(['business', 'startup'])
    .by_content_length(min_length=50)
    .apply(notes))

# Sort notes
sorted_notes = NoteSorter.by_date(filtered_notes, ascending=False)

# Create backup
backup_mgr = BackupManager()
backup_file = backup_mgr.create_backup('path/to/plum.sqlite')

# Generate analytics
analytics = AdvancedAnalytics()
word_freq = analytics.get_word_frequency(notes, top_n=20)
category_stats = analytics.get_category_stats(categorized)

# Export to multiple formats
export_manager = ExportManager('my_output')
results = export_manager.export(sorted_notes, ['csv', 'json'], 'filtered_notes')
```

### Custom Categories

```python
# Add custom category
categorizer = NoteCategorizer()
categorizer.add_custom_category('Recipes', ['recipe', 'cooking', 'ingredients', 'food'])

# Use in categorization
categorized = categorizer.categorize_notes(notes)
```

## 🖥️ Database Support

### Supported Formats

- **Modern Sticky Notes** (Windows 10/11): `plum.sqlite` ✅
- **Classic Sticky Notes** (Windows 7/8/early 10): `StickyNotes.snt` ✅ **NEW in v1.1.0!**

### Auto-Detection Locations

The tool automatically searches these locations:

**Windows:**
- `%USERPROFILE%\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite`
- `%USERPROFILE%\AppData\Roaming\Microsoft\Sticky Notes\StickyNotes.snt`

**Current Directory:**
- `./plum.sqlite`
- `./StickyNotes.snt`

## 📋 Requirements

### Core Dependencies

```
click>=8.0.0              # CLI framework
pandas>=1.3.0             # DataFrames (optional, for Excel)
openpyxl>=3.0.0           # Excel writer (optional)
colorama>=0.4.0           # Colored console output
tabulate>=0.8.0           # Table formatting
pathlib2>=2.3.0           # Path handling
python-dateutil>=2.8.0    # Date utilities
```

### GUI Dependencies

```
matplotlib>=3.5.0         # Charts and visualizations
Pillow>=9.0.0            # Image handling
wordcloud>=1.8.0         # Word cloud generation
```

All dependencies are automatically installed via `install.py` or `requirements.txt`.

## 🛠️ Development

### Project Structure

```
sticky-note-organizer/
├── src/sticky_organizer/          # Main package
│   ├── __init__.py                # Package initialization
│   ├── cli.py                     # Command-line interface
│   ├── gui.py                     # GUI application
│   ├── gui_launcher.py            # GUI entry point
│   ├── database.py                # Database operations
│   ├── categorizer.py             # Note categorization
│   ├── exporters.py               # Export functionality
│   ├── filters.py                 # Advanced filtering
│   ├── backup.py                  # Backup/restore operations
│   ├── analytics.py               # Analytics and statistics
│   └── editor.py                  # Note editing operations
├── tests/                         # Test files
├── docs/                          # Documentation
├── examples/                      # Usage examples
├── requirements.txt               # Dependencies
├── setup.py                       # Package setup
├── install.py                     # Installation script
├── StickyNoteOrganizer.pyw        # GUI launcher (no console)
├── launch_gui.bat                 # Windows batch launcher
├── launch_gui.py                  # Python launcher
└── README.md                      # This file
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=sticky_organizer

# Run specific test file
python -m pytest tests/test_categorizer.py
```

### Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Write tests for new features
   - Update documentation
   - Follow PEP 8 style guidelines
4. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

#### Development Guidelines

- Write clear, descriptive commit messages
- Add tests for all new features
- Update documentation for any API changes
- Ensure all tests pass before submitting PR
- Follow the existing code style

## 🐛 Troubleshooting

### GUI won't launch

Make sure GUI dependencies are installed:
```bash
pip install matplotlib Pillow wordcloud
```

### Database not found

The tool looks for the database in standard Windows locations. If not found:
1. Use the GUI's "Connect" button to manually select the database
2. Or use `--db-path` option in CLI commands

### Export fails

- **Excel export**: Install pandas and openpyxl: `pip install pandas openpyxl`
- **Permission errors**: Check that the output directory is writable

### Backup/Restore issues

- Ensure you have write permissions in the backup directory
- Verify the backup file exists and is not corrupted
- For ZIP backups, ensure the file is a valid ZIP archive

### Console encoding errors

If you see Unicode errors on Windows:
- The tool automatically handles encoding issues with multiple fallback levels
- If problems persist, use the GUI instead of CLI
- Or redirect output: `sticky-organizer extract > output.log 2>&1`

## 📊 Example Output

```
EXTRACTION SUMMARY
==================================================
Total notes extracted: 371
Categories found: 13

CATEGORY BREAKDOWN:
  Miscellaneous              75 notes ( 20.2%)
  Business Ideas             72 notes ( 19.4%)
  Financial/Money            59 notes ( 15.9%)
  Technology/Development     58 notes ( 15.6%)
  Contacts/People            30 notes (  8.1%)
  Work/Career                25 notes (  6.7%)
  Tasks/Reminders            21 notes (  5.7%)
  Personal Goals             10 notes (  2.7%)
  Travel/Places               8 notes (  2.2%)
  Shopping/Items              6 notes (  1.6%)
  Ideas/Thoughts              4 notes (  1.1%)
  Education/Learning          2 notes (  0.5%)
  Health/Fitness              1 notes (  0.3%)
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Microsoft for the Sticky Notes application
- The Python community for excellent libraries
- All contributors and users of this tool

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/Primus-Izzy/Sticky-Note-Organizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Primus-Izzy/Sticky-Note-Organizer/discussions)

## 🗺️ Roadmap

- [x] Support for Classic Sticky Notes (.snt format) ✅ **v1.1.0**
- [ ] Cloud sync support
- [ ] Mobile app companion
- [ ] Advanced AI-powered categorization
- [ ] Collaborative features
- [ ] Theme customization
- [ ] Export to OneNote/Evernote

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

Made with ❤️ for better note organization

</div>
