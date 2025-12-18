# Contributing to Sticky Note Organizer

First off, thank you for considering contributing to Sticky Note Organizer! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title** for the issue
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples** to demonstrate the steps
* **Describe the behavior you observed** and what behavior you expected
* **Include screenshots** if relevant
* **Include your environment details**:
  - OS version (Windows 10/11)
  - Python version
  - Package version

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description** of the suggested enhancement
* **Explain why this enhancement would be useful** to most users
* **List any alternatives** you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes**:
   - If you've added code, add tests
   - If you've changed APIs, update the documentation
   - Ensure the test suite passes
   - Make sure your code follows the existing style
3. **Commit your changes** with clear, descriptive commit messages
4. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Windows OS (for testing full functionality)

### Setting Up Your Development Environment

1. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/sticky-note-organizer.git
   cd sticky-note-organizer
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Install development dependencies:**
   ```bash
   pip install pytest pytest-cov black flake8
   ```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=sticky_organizer

# Run specific test file
python -m pytest tests/test_categorizer.py -v
```

### Code Style

This project follows PEP 8 style guidelines. Before submitting your code:

```bash
# Format code with black
black src/

# Check style with flake8
flake8 src/ --max-line-length=100
```

## Project Structure

```
sticky-note-organizer/
├── src/sticky_organizer/     # Main source code
│   ├── cli.py               # Command-line interface
│   ├── gui.py               # GUI application
│   ├── database.py          # Database operations
│   ├── categorizer.py       # Note categorization logic
│   ├── exporters.py         # Export functionality
│   ├── filters.py           # Filtering and sorting
│   ├── backup.py            # Backup/restore operations
│   ├── analytics.py         # Analytics and statistics
│   └── editor.py            # Note editing operations
├── tests/                    # Test files
├── docs/                     # Documentation
└── examples/                 # Usage examples
```

## Coding Guidelines

### General Principles

- **Keep it simple**: Write clear, readable code
- **DRY (Don't Repeat Yourself)**: Extract common functionality
- **Test your code**: Add tests for new features
- **Document your code**: Add docstrings for classes and functions

### Python Style

```python
# Good: Clear function with docstring
def categorize_note(content: str) -> str:
    """
    Categorize a single note based on its content.

    Args:
        content: The note content to categorize

    Returns:
        The category name as a string
    """
    if not content:
        return 'Miscellaneous'
    # Implementation...
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Examples:
```
Add note merging functionality

- Implement merge_notes() method in NoteEditor
- Add CLI command for merging
- Add tests for merge functionality
- Update documentation

Fixes #123
```

### Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use descriptive test names

```python
def test_categorize_empty_content():
    """Test that empty content is categorized as Miscellaneous"""
    categorizer = NoteCategorizer()
    result = categorizer.categorize_note("")
    assert result == 'Miscellaneous'
```

## Adding New Features

### Adding a New Export Format

1. Create an exporter class in `src/sticky_organizer/exporters.py`:
   ```python
   class YourFormatExporter(BaseExporter):
       def export(self, notes, output_path, filename):
           # Implementation
   ```

2. Register it in `ExportManager.export()`:
   ```python
   if 'yourformat' in formats:
       exporter = YourFormatExporter(output_dir)
       # ...
   ```

3. Add tests in `tests/test_exporters.py`
4. Update documentation in `README.md`

### Adding a New Category

1. Add category keywords in `src/sticky_organizer/categorizer.py`:
   ```python
   self.categories = {
       'Your Category': ['keyword1', 'keyword2', ...],
       # ...
   }
   ```

2. Add tests in `tests/test_categorizer.py`
3. Update documentation

### Adding a New CLI Command

1. Add command in `src/sticky_organizer/cli.py`:
   ```python
   @cli.command()
   @click.option(...)
   def your_command(...):
       """Command description"""
       # Implementation
   ```

2. Add tests
3. Update README with command documentation

## Documentation

- Update README.md for user-facing changes
- Add docstrings for all public functions and classes
- Include code examples in docstrings
- Update docs/ directory for major features

## Release Process

(For maintainers)

1. Update version number in `setup.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Build and upload to PyPI (if applicable)

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- GitHub contributors page
- Release notes

Thank you for contributing! 🎉
