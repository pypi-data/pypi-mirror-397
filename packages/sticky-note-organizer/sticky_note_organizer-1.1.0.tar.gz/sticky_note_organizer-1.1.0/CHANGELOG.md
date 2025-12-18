# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-15

### Added

#### Classic Sticky Notes Support
- **Full support for .snt file format** (Windows 7/8/early 10)
  - New `ClassicStickyNotesParser` class for parsing .snt files
  - Extracts text content from RTF-formatted classic sticky notes
  - Supports multiple encoding methods (UTF-8, UTF-16, Latin-1)
  - Automatic detection and handling of classic .snt format
- **Updated database auto-detection** to find .snt files
  - Searches standard Windows 7/8 locations
  - Supports both `StickyNotes.snt` and `ThresholdNotes.snt`
- **Seamless integration** with existing tools
  - Works with all CLI commands
  - Works with GUI interface
  - Same export formats available
  - Same categorization system applies

### Changed
- Enhanced `StickyNotesDatabase.connect()` to handle .snt files
- Enhanced `StickyNotesDatabase.extract_notes()` to parse .snt format
- Updated documentation to reflect .snt support

### Technical Details
- **Binary format parsing** for proprietary .snt structure
- **RTF content extraction** with multiple fallback methods
- **Robust error handling** for corrupted or unusual .snt files
- **Backward compatible** - existing functionality unchanged

---

## [1.0.0] - 2024-12-15

### Added

#### GUI Features
- **Full Tkinter-based GUI application** with 5 main tabs
  - Browser tab for viewing and editing notes
  - Filter tab with advanced filtering and live preview
  - Statistics tab with charts and analytics
  - Backup tab for backup/restore operations
  - Settings tab for configuration
- **Easy GUI launchers** for non-technical users
  - `StickyNoteOrganizer.pyw` - Windows launcher without console
  - `launch_gui.bat` - Batch file launcher
  - `launch_gui.py` - Python launcher script
- **Visual statistics dashboard** with matplotlib charts
  - Category distribution pie chart
  - Word frequency analysis
  - Timeline charts
- **Note management features**
  - Edit notes directly in GUI
  - Delete notes with confirmation
  - Merge multiple notes
  - Find duplicate notes

#### Core Features
- **Backup and restore functionality**
  - Create compressed ZIP backups
  - Restore from backup with safety backup
  - List and manage backups
  - Automatic backup before destructive operations
- **Advanced filtering system**
  - Filter by date range
  - Filter by categories (multiple selection)
  - Filter by content length
  - Filter by keywords
  - Filter by theme/color
  - Chainable filter API
- **Note editing capabilities**
  - Edit note content
  - Merge multiple notes with separator
  - Delete notes safely
  - Bulk categorization
- **Analytics and insights**
  - Word frequency analysis with stop words filtering
  - Category statistics
  - Timeline analysis
  - Duplicate detection using Jaccard similarity

#### CLI Commands
- `sticky-organizer backup` - Create database backup
- `sticky-organizer restore` - Restore from backup
- `sticky-organizer edit` - Edit note by ID
- `sticky-organizer merge` - Merge multiple notes
- `sticky-organizer gui` - Launch GUI application

#### Documentation
- Comprehensive README.md with GUI guide
- CONTRIBUTING.md for contributors
- Detailed CLI command reference
- API usage examples
- Troubleshooting guide

### Changed
- **Improved categorization accuracy**
  - Fixed contact detection to check before URL patterns
  - Better regex patterns for phone numbers and emails
  - Improved keyword matching
- **Enhanced Windows console support**
  - Multi-level encoding fallback system
  - Graceful degradation from colored → plain → ASCII output
  - Added flush=True to prevent buffer issues
  - Handles cp1252 encoding properly
- **Better error handling**
  - Try-except blocks for encoding errors
  - Validation for note IDs and paths
  - User-friendly error messages

### Fixed
- **Windows console encoding issues** - Fixed UnicodeEncodeError and OSError when piping output
- **Summary export parameter mismatch** - Fixed 'list' object has no attribute 'items' error
- **None content handling** - Fixed AttributeError when note content is None
- **Contact categorization** - Improved to correctly categorize notes with emails/phones
- **Unicode character handling** - Robust handling of special characters in note content

### Technical Improvements
- Added context manager support for NoteEditor
- Fluent API for filters with method chaining
- Separate exporters for different formats
- Comprehensive test suite (25 unit tests + 7 integration tests)
- 100% test pass rate

## [0.1.0] - Initial Release

### Added
- Basic CLI functionality
- Note extraction from Microsoft Sticky Notes database
- Automatic categorization into 12+ categories
- Export to CSV, JSON, Markdown formats
- Basic search functionality
- Database auto-detection
- Console colored output

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
