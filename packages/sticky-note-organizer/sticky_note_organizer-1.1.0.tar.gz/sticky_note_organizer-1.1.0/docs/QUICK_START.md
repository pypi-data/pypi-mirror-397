# Quick Start Guide

Get started with Sticky Note Organizer in just a few minutes!

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/sticky-note-organizer.git
cd sticky-note-organizer
```

### Step 2: Install

**Easy Installation (Recommended):**
```bash
python install.py
```

**Manual Installation:**
```bash
pip install -r requirements.txt
pip install -e .
```

### Step 3: Verify Installation

```bash
sticky-organizer --version
```

## First Run

### GUI Mode (Easiest for Beginners)

**Method 1: Double-Click**
1. Open File Explorer
2. Navigate to the project folder
3. Double-click `StickyNoteOrganizer.pyw`
4. The GUI opens automatically!

**Method 2: Command Line**
```bash
sticky-organizer-gui
```

### CLI Mode (For Power Users)

#### Check Your Database

```bash
sticky-organizer info
```

This will show:
- Database location
- Number of notes
- Database size
- Table structure

#### Extract Your Notes

```bash
sticky-organizer extract
```

This creates an `output` folder with:
- `sticky_notes.csv` - All your notes in CSV format
- Category-organized data

#### Search Your Notes

```bash
sticky-organizer search "meeting"
```

Find notes containing specific keywords.

## Common Tasks

### Task 1: Backup Your Notes

**GUI:**
1. Launch GUI
2. Click "Backup" tab
3. Click "Create Backup Now"

**CLI:**
```bash
sticky-organizer backup
```

### Task 2: Export to Multiple Formats

**GUI:**
1. Launch GUI
2. Go to "Browser" tab
3. Select export format buttons (CSV, JSON, Excel, Markdown)

**CLI:**
```bash
sticky-organizer extract -f csv json excel markdown summary
```

### Task 3: Filter Notes

**GUI:**
1. Launch GUI
2. Go to "Filter" tab
3. Set your criteria:
   - Date range
   - Categories
   - Keywords
   - Content length
4. Click "Apply Filter"

**CLI:**
```bash
# Search specific category
sticky-organizer search "project" -c "Work/Career"

# Case-sensitive search
sticky-organizer search "API" --case-sensitive
```

### Task 4: Edit a Note

**GUI:**
1. Launch GUI
2. Go to "Browser" tab
3. Select a category
4. Click on a note
5. Edit in the text area
6. Click "Save Changes"

**CLI:**
```bash
sticky-organizer edit [note-id] "New content here"
```

### Task 5: Merge Notes

**GUI:**
1. Launch GUI
2. Go to "Browser" tab
3. Select notes to merge
4. Right-click → Merge

**CLI:**
```bash
sticky-organizer merge [note-id-1] [note-id-2] [note-id-3]
```

### Task 6: View Statistics

**GUI:**
1. Launch GUI
2. Go to "Statistics" tab
3. Click "Generate Statistics"
4. View charts and insights

**CLI:**
```bash
sticky-organizer info
sticky-organizer categories
```

## Tips and Tricks

### Tip 1: Automatic Backup Before Editing

The tool automatically creates a backup before any destructive operation (edit, merge, delete).

### Tip 2: Custom Output Directory

```bash
sticky-organizer extract -o my_notes_folder
```

### Tip 3: Specify Database Path

If the auto-detection doesn't work:

```bash
sticky-organizer extract -d "C:\path\to\plum.sqlite"
```

**Or in GUI:**
1. Click "Connect" button
2. Browse to your database file

### Tip 4: Export Only Summary

```bash
sticky-organizer extract -f summary --no-stats
```

### Tip 5: Create Custom Categories

**In Python:**
```python
from sticky_organizer.categorizer import NoteCategorizer

categorizer = NoteCategorizer()
categorizer.add_custom_category('Recipes', ['recipe', 'cooking', 'food', 'ingredients'])
```

## Troubleshooting

### Issue: Database Not Found

**Solution:**
1. Verify Microsoft Sticky Notes is installed
2. Create at least one sticky note
3. Check standard location:
   ```
   %USERPROFILE%\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite
   ```
4. Use manual path: `sticky-organizer extract -d "path\to\plum.sqlite"`

### Issue: GUI Won't Launch

**Solution:**
```bash
pip install matplotlib Pillow wordcloud
```

### Issue: Export Permission Error

**Solution:**
1. Run as administrator
2. Or change output directory: `sticky-organizer extract -o C:\Users\YourName\Documents\notes`

### Issue: Python Not Found

**Solution:**
1. Install Python 3.7+ from python.org
2. During installation, check "Add Python to PATH"
3. Restart your terminal

## Next Steps

Now that you're set up:

1. **Explore the GUI** - Browse all five tabs to see all features
2. **Read the README** - For detailed documentation
3. **Check Examples** - See `examples/` folder for usage examples
4. **Customize Categories** - Add your own categories in Settings
5. **Create Regular Backups** - Schedule weekly backups

## Getting Help

- **Documentation**: See `README.md` and other docs in `docs/`
- **Issues**: Report problems on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions

Happy organizing! 📝✨
