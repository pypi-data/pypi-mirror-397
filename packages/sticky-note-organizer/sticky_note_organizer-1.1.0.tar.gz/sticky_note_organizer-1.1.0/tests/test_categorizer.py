"""
Tests for the note categorizer
"""

import pytest
from sticky_organizer.categorizer import NoteCategorizer


class TestNoteCategorizer:
    """Test the NoteCategorizer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.categorizer = NoteCategorizer()
        
    def test_categorize_business_note(self):
        """Test categorizing a business-related note"""
        content = "I have a great startup idea for a new app that helps businesses with marketing"
        category = self.categorizer.categorize_note(content)
        assert category == "Business Ideas"
        
    def test_categorize_financial_note(self):
        """Test categorizing a financial note"""
        content = "Need to pay $500 rent tomorrow and check my bank account balance"
        category = self.categorizer.categorize_note(content)
        assert category == "Financial/Money"
        
    def test_categorize_tech_note(self):
        """Test categorizing a technology note"""
        content = "Check out this API documentation at https://api.example.com/docs"
        category = self.categorizer.categorize_note(content)
        assert category == "Technology/Development"
        
    def test_categorize_contact_note(self):
        """Test categorizing a contact note"""
        content = "John Smith - john@example.com - 555-123-4567"
        category = self.categorizer.categorize_note(content)
        assert category == "Contacts/People"
        
    def test_categorize_work_note(self):
        """Test categorizing a work-related note"""
        content = "Meeting with the team tomorrow at 2 PM to discuss project deadlines"
        category = self.categorizer.categorize_note(content)
        assert category == "Work/Career"
        
    def test_categorize_miscellaneous_note(self):
        """Test categorizing a note that doesn't fit specific categories"""
        content = "The weather is nice today"
        category = self.categorizer.categorize_note(content)
        assert category == "Miscellaneous"
        
    def test_categorize_multiple_notes(self):
        """Test categorizing multiple notes"""
        notes = [
            {'content': 'Business meeting about new product launch', 'id': '1'},
            {'content': 'Buy groceries: milk, bread, eggs', 'id': '2'},
            {'content': 'Learn Python programming this weekend', 'id': '3'}
        ]
        
        categorized = self.categorizer.categorize_notes(notes)
        
        # Check that notes are properly categorized
        assert len(categorized) > 0
        
        # Check that each note has a category assigned
        for category_notes in categorized.values():
            for note in category_notes:
                assert 'category' in note
                
    def test_add_custom_category(self):
        """Test adding custom categories"""
        self.categorizer.add_custom_category('Recipes', ['recipe', 'cooking', 'ingredients'])
        
        content = "Great recipe for chocolate chip cookies with these ingredients"
        category = self.categorizer.categorize_note(content)
        assert category == "Recipes"
        
    def test_get_categories(self):
        """Test getting all categories"""
        categories = self.categorizer.get_categories()
        
        # Check that default categories exist
        assert "Business Ideas" in categories
        assert "Financial/Money" in categories
        assert "Technology/Development" in categories
        
        # Check that categories have keywords
        for category, keywords in categories.items():
            assert len(keywords) > 0
            assert all(isinstance(keyword, str) for keyword in keywords)
            
    def test_empty_content(self):
        """Test categorizing empty content"""
        category = self.categorizer.categorize_note("")
        assert category == "Miscellaneous"
        
    def test_none_content(self):
        """Test categorizing None content"""
        notes = [{'content': None, 'id': '1'}]
        categorized = self.categorizer.categorize_notes(notes)
        
        # Should handle gracefully without errors
        assert len(categorized) >= 0