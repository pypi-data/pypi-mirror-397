#!/usr/bin/env python3
"""
Basic Usage Examples for Sticky Note Organizer

This script demonstrates common usage patterns for the Sticky Note Organizer library.
"""

from sticky_organizer.database import StickyNotesDatabase
from sticky_organizer.categorizer import NoteCategorizer
from sticky_organizer.exporters import ExportManager
from sticky_organizer.filters import NoteFilter, NoteSorter
from sticky_organizer.backup import BackupManager
from sticky_organizer.analytics import AdvancedAnalytics


def example_1_basic_extraction():
    """Example 1: Basic note extraction"""
    print("=" * 50)
    print("Example 1: Basic Note Extraction")
    print("=" * 50)

    # Connect to database
    db = StickyNotesDatabase()
    if db.connect():
        print(f"✓ Connected to database")

        # Extract notes
        notes = db.extract_notes()
        print(f"✓ Extracted {len(notes)} notes")

        # Close connection
        db.close()
        print("✓ Database closed")
    else:
        print("✗ Could not connect to database")


def example_2_categorization():
    """Example 2: Note categorization"""
    print("\n" + "=" * 50)
    print("Example 2: Note Categorization")
    print("=" * 50)

    # Get notes
    db = StickyNotesDatabase()
    if not db.connect():
        return

    notes = db.extract_notes()
    db.close()

    # Categorize notes
    categorizer = NoteCategorizer()
    categorized = categorizer.categorize_notes(notes)

    # Print category summary
    print(f"\nFound {len(categorized)} categories:")
    for category, category_notes in categorized.items():
        print(f"  {category}: {len(category_notes)} notes")


def example_3_filtering():
    """Example 3: Advanced filtering"""
    print("\n" + "=" * 50)
    print("Example 3: Advanced Filtering")
    print("=" * 50)

    # Get notes
    db = StickyNotesDatabase()
    if not db.connect():
        return

    notes = db.extract_notes()
    db.close()

    # Create filter
    filter_engine = NoteFilter()

    # Apply multiple filters (chainable)
    filtered_notes = (filter_engine
        .by_content_length(min_length=50)  # At least 50 characters
        .by_keywords(['business', 'startup', 'idea'])  # Contains these keywords
        .apply(notes))

    print(f"✓ Filtered from {len(notes)} to {len(filtered_notes)} notes")

    # Sort by date (most recent first)
    sorted_notes = NoteSorter.by_date(filtered_notes, ascending=False)

    # Show first 5
    print("\nTop 5 recent business notes:")
    for i, note in enumerate(sorted_notes[:5], 1):
        content_preview = note['content'][:60] + "..." if len(note['content']) > 60 else note['content']
        print(f"{i}. {content_preview}")


def example_4_export():
    """Example 4: Export to multiple formats"""
    print("\n" + "=" * 50)
    print("Example 4: Export to Multiple Formats")
    print("=" * 50)

    # Get notes
    db = StickyNotesDatabase()
    if not db.connect():
        return

    notes = db.extract_notes()
    db.close()

    # Add categories to notes
    categorizer = NoteCategorizer()
    for note in notes:
        note['category'] = categorizer.categorize_note(note.get('content', ''))

    # Export to multiple formats
    export_manager = ExportManager('example_output')
    results = export_manager.export(notes, ['csv', 'json'], 'my_notes')

    print("✓ Exported notes:")
    for result in results:
        if result['success']:
            print(f"  ✓ {result['format'].upper()}: {result['path']}")
        else:
            print(f"  ✗ {result['format'].upper()}: {result['error']}")


def example_5_backup():
    """Example 5: Create backup"""
    print("\n" + "=" * 50)
    print("Example 5: Create Backup")
    print("=" * 50)

    # Find database
    db = StickyNotesDatabase()
    if not db.connect():
        print("✗ Could not find database")
        return

    db_path = db.db_path
    db.close()

    # Create backup
    backup_mgr = BackupManager('example_backups')
    try:
        backup_file = backup_mgr.create_backup(str(db_path), compress=True)
        print(f"✓ Backup created: {backup_file}")

        # List all backups
        backups = backup_mgr.list_backups()
        print(f"\nTotal backups: {len(backups)}")

    except Exception as e:
        print(f"✗ Backup failed: {e}")


def example_6_analytics():
    """Example 6: Analytics and insights"""
    print("\n" + "=" * 50)
    print("Example 6: Analytics and Insights")
    print("=" * 50)

    # Get notes
    db = StickyNotesDatabase()
    if not db.connect():
        return

    notes = db.extract_notes()
    db.close()

    # Create analytics
    analytics = AdvancedAnalytics()

    # Get word frequency
    word_freq = analytics.get_word_frequency(notes, top_n=10)
    print("\nTop 10 most common words:")
    for word, count in word_freq:
        print(f"  {word}: {count}")

    # Categorize for stats
    categorizer = NoteCategorizer()
    categorized = categorizer.categorize_notes(notes)

    # Get category stats
    category_stats = analytics.get_category_stats(categorized)
    print(f"\nCategory Statistics:")
    print(f"  Total categories: {category_stats['total_categories']}")
    print(f"  Largest category: {category_stats['largest_category']}")
    print(f"  Average notes per category: {category_stats['avg_notes_per_category']:.1f}")


def example_7_custom_categories():
    """Example 7: Custom categories"""
    print("\n" + "=" * 50)
    print("Example 7: Custom Categories")
    print("=" * 50)

    # Create categorizer with custom category
    categorizer = NoteCategorizer()

    # Add custom category
    categorizer.add_custom_category(
        'Recipes',
        ['recipe', 'cooking', 'ingredients', 'bake', 'cook', 'food', 'dish']
    )

    # Test categorization
    test_notes = [
        "Here's my favorite chocolate cake recipe with ingredients...",
        "Meeting tomorrow at 3pm to discuss the project",
        "Need to buy eggs and flour for cooking tonight"
    ]

    print("\nCategorizing test notes:")
    for note in test_notes:
        category = categorizer.categorize_note(note)
        preview = note[:50] + "..." if len(note) > 50 else note
        print(f"  [{category}] {preview}")


def main():
    """Run all examples"""
    print("Sticky Note Organizer - Usage Examples\n")

    try:
        example_1_basic_extraction()
        example_2_categorization()
        example_3_filtering()
        example_4_export()
        example_5_backup()
        example_6_analytics()
        example_7_custom_categories()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
