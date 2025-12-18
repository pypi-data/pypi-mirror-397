"""
Test configuration and fixtures for pytest
"""

import pytest
import tempfile
import sqlite3
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_database(temp_dir):
    """Create a sample SQLite database for testing"""
    db_path = temp_dir / "test_plum.sqlite"
    
    # Create a simple database structure similar to plum.sqlite
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create Note table
    cursor.execute('''
        CREATE TABLE Note (
            Id TEXT PRIMARY KEY,
            Text TEXT,
            CreatedAt INTEGER,
            UpdatedAt INTEGER,
            Theme TEXT,
            Type TEXT,
            DeletedAt INTEGER
        )
    ''')
    
    # Insert sample data
    sample_notes = [
        ('note1', 'This is a business idea about startup ventures', 
         638000000000000000, 638000000000000000, 'Yellow', 'Note', None),
        ('note2', 'Need to pay $500 rent tomorrow', 
         638100000000000000, 638100000000000000, 'Blue', 'Note', None),
        ('note3', 'Contact: john@example.com, phone: 555-1234', 
         638200000000000000, 638200000000000000, 'Green', 'Note', None),
        ('note4', 'Deleted note should not appear', 
         638300000000000000, 638300000000000000, 'Red', 'Note', 638400000000000000)  # This one is deleted
    ]
    
    cursor.executemany('''
        INSERT INTO Note (Id, Text, CreatedAt, UpdatedAt, Theme, Type, DeletedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_notes)
    
    conn.commit()
    conn.close()
    
    yield db_path


@pytest.fixture
def sample_notes():
    """Sample notes data for testing"""
    return [
        {
            'id': 'note1',
            'content': 'This is a business idea about startup ventures and marketing strategies',
            'created_date': '2023-06-15 10:30:00',
            'updated_date': '2023-06-15 10:30:00',
            'theme': 'Yellow',
            'type': 'Note',
            'category': 'Business Ideas'
        },
        {
            'id': 'note2',
            'content': 'Need to pay $500 rent tomorrow and check bank balance',
            'created_date': '2023-07-20 14:15:00',
            'updated_date': '2023-07-20 14:15:00',
            'theme': 'Blue',
            'type': 'Note',
            'category': 'Financial/Money'
        },
        {
            'id': 'note3',
            'content': 'john@example.com, phone: 555-1234, address: 123 Main St',
            'created_date': '2023-08-10 09:00:00',
            'updated_date': '2023-08-10 09:00:00',
            'theme': 'Green',
            'type': 'Note',
            'category': 'Contacts/People'
        },
        {
            'id': 'note4',
            'content': 'Short note',
            'created_date': '2023-09-05 16:45:00',
            'updated_date': '2023-09-05 16:45:00',
            'theme': 'Pink',
            'type': 'Note',
            'category': 'Miscellaneous'
        }
    ]


@pytest.fixture
def categorized_notes():
    """Sample categorized notes for testing"""
    return {
        'Business Ideas': [
            {
                'id': 'note1',
                'content': 'Startup idea for mobile app development',
                'created_date': '2023-06-15 10:30:00',
                'category': 'Business Ideas'
            },
            {
                'id': 'note5',
                'content': 'Marketing strategy for social media campaigns',
                'created_date': '2023-06-20 11:00:00',
                'category': 'Business Ideas'
            }
        ],
        'Financial/Money': [
            {
                'id': 'note2',
                'content': 'Budget planning for next month - $2000 income, $1500 expenses',
                'created_date': '2023-07-01 09:15:00',
                'category': 'Financial/Money'
            }
        ],
        'Technology/Development': [
            {
                'id': 'note3',
                'content': 'Learn Python web development with Django framework',
                'created_date': '2023-08-10 14:30:00',
                'category': 'Technology/Development'
            }
        ]
    }