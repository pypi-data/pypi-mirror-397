"""
Tests for the note filters
"""

import pytest
from datetime import datetime, timedelta
from sticky_organizer.filters import NoteFilter, NoteSorter, NoteAnalyzer


class TestNoteFilter:
    """Test the NoteFilter class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.filter = NoteFilter()
        self.sample_notes = [
            {
                'content': 'This is a long note about business ideas and startup concepts',
                'created_date': '2023-06-15 10:30:00',
                'category': 'Business Ideas',
                'theme': 'Yellow'
            },
            {
                'content': 'Short note',
                'created_date': '2023-07-20 14:15:00',
                'category': 'Miscellaneous',
                'theme': 'Blue'
            },
            {
                'content': 'Contact: john@example.com, phone: 555-1234',
                'created_date': '2023-08-10 09:00:00',
                'category': 'Contacts/People',
                'theme': 'Green'
            }
        ]
    
    def test_filter_by_content_length(self):
        """Test filtering by content length"""
        # Filter for notes with at least 20 characters
        filtered = self.filter.by_content_length(min_length=20).apply(self.sample_notes)
        
        assert len(filtered) == 2  # Two notes are longer than 20 characters
        assert all(len(note['content']) >= 20 for note in filtered)
        
    def test_filter_by_date_range(self):
        """Test filtering by date range"""
        # Filter for notes from July 2023
        filtered = self.filter.reset().by_date_range('2023-07-01', '2023-07-31').apply(self.sample_notes)
        
        assert len(filtered) == 1
        assert '2023-07-20' in filtered[0]['created_date']
        
    def test_filter_by_theme(self):
        """Test filtering by theme"""
        filtered = self.filter.reset().by_theme(['Yellow', 'Green']).apply(self.sample_notes)
        
        assert len(filtered) == 2
        themes = [note['theme'] for note in filtered]
        assert 'Yellow' in themes
        assert 'Green' in themes
        
    def test_filter_by_category(self):
        """Test filtering by category"""
        filtered = self.filter.reset().by_category(['Business Ideas']).apply(self.sample_notes)
        
        assert len(filtered) == 1
        assert filtered[0]['category'] == 'Business Ideas'
        
    def test_filter_by_keywords(self):
        """Test filtering by keywords"""
        # Filter for notes containing 'business' or 'contact'
        filtered = self.filter.reset().by_keywords(['business', 'contact']).apply(self.sample_notes)
        
        assert len(filtered) == 2  # One has 'business', one has 'Contact'
        
    def test_filter_by_has_emails(self):
        """Test filtering notes that contain email addresses"""
        filtered = self.filter.reset().by_has_emails().apply(self.sample_notes)
        
        assert len(filtered) == 1
        assert 'john@example.com' in filtered[0]['content']
        
    def test_chain_filters(self):
        """Test chaining multiple filters"""
        filtered = (self.filter.reset()
                   .by_content_length(min_length=10)
                   .by_theme(['Yellow', 'Green'])
                   .apply(self.sample_notes))
        
        assert len(filtered) == 2
        assert all(len(note['content']) >= 10 for note in filtered)
        assert all(note['theme'] in ['Yellow', 'Green'] for note in filtered)


class TestNoteSorter:
    """Test the NoteSorter class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sample_notes = [
            {
                'content': 'Short',
                'created_date': '2023-08-10 09:00:00',
                'category': 'B Category'
            },
            {
                'content': 'This is a much longer note with more content',
                'created_date': '2023-06-15 10:30:00',
                'category': 'A Category'
            },
            {
                'content': 'Medium length note',
                'created_date': '2023-07-20 14:15:00',
                'category': 'C Category'
            }
        ]
    
    def test_sort_by_date_ascending(self):
        """Test sorting by date in ascending order"""
        sorted_notes = NoteSorter.by_date(self.sample_notes, ascending=True)
        
        dates = [note['created_date'] for note in sorted_notes]
        assert dates == sorted(dates)
        
    def test_sort_by_date_descending(self):
        """Test sorting by date in descending order"""
        sorted_notes = NoteSorter.by_date(self.sample_notes, ascending=False)
        
        dates = [note['created_date'] for note in sorted_notes]
        assert dates == sorted(dates, reverse=True)
        
    def test_sort_by_length(self):
        """Test sorting by content length"""
        sorted_notes = NoteSorter.by_length(self.sample_notes, ascending=True)
        
        lengths = [len(note['content']) for note in sorted_notes]
        assert lengths == sorted(lengths)
        
    def test_sort_by_category(self):
        """Test sorting by category"""
        sorted_notes = NoteSorter.by_category(self.sample_notes, ascending=True)
        
        categories = [note['category'] for note in sorted_notes]
        assert categories == sorted(categories)


class TestNoteAnalyzer:
    """Test the NoteAnalyzer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sample_notes = [
            {'content': 'This is a test note about business and marketing'},
            {'content': 'Another test note about business development'},
            {'content': 'A note about cooking and recipes'}
        ]
        
        self.categorized_notes = {
            'Business': [
                {'content': 'Business note 1', 'created_date': '2023-06-15 10:30:00'},
                {'content': 'Business note 2', 'created_date': '2023-07-20 14:15:00'}
            ],
            'Cooking': [
                {'content': 'Recipe for cookies', 'created_date': '2023-08-10 09:00:00'}
            ]
        }
    
    def test_get_word_frequency(self):
        """Test getting word frequency from notes"""
        word_freq = NoteAnalyzer.get_word_frequency(self.sample_notes, top_n=5)
        
        # Should return list of tuples (word, count)
        assert isinstance(word_freq, list)
        assert len(word_freq) <= 5
        
        if word_freq:
            assert isinstance(word_freq[0], tuple)
            assert len(word_freq[0]) == 2
            
            # 'business' should appear twice
            word_counts = dict(word_freq)
            assert word_counts.get('business', 0) == 2
    
    def test_get_category_stats(self):
        """Test getting statistics for each category"""
        stats = NoteAnalyzer.get_category_stats(self.categorized_notes)
        
        # Should have stats for each category
        assert 'Business' in stats
        assert 'Cooking' in stats
        
        business_stats = stats['Business']
        assert business_stats['count'] == 2
        assert business_stats['avg_length'] > 0
        assert business_stats['min_length'] > 0
        assert business_stats['max_length'] > 0
        
    def test_find_duplicates(self):
        """Test finding duplicate notes"""
        notes_with_duplicates = [
            {'content': 'This is a unique note'},
            {'content': 'This is a duplicate note'},
            {'content': 'This is a duplicate note'},  # Exact duplicate
            {'content': 'Another unique note'}
        ]
        
        duplicates = NoteAnalyzer.find_duplicates(notes_with_duplicates)
        
        # Should find one group of duplicates
        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2  # Two identical notes
        
        # Both duplicates should have the same content
        duplicate_group = duplicates[0]
        assert duplicate_group[0]['content'] == duplicate_group[1]['content']