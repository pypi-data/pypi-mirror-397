"""
Database detection and handling for Microsoft Sticky Notes
"""

import os
import sqlite3
import platform
import struct
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime


class ClassicStickyNotesParser:
    """Parser for classic Sticky Notes .snt format (Windows 7/8)"""

    @staticmethod
    def extract_notes_from_snt(file_path: str) -> List[Dict[str, Any]]:
        """
        Extract notes from classic .snt file format.
        The .snt file is an OLE compound document containing RTF data.
        """
        notes = []

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            # Look for RTF content markers and note separators
            # Classic sticky notes store data in RTF format
            rtf_pattern = rb'\\rtf1[^}]*?\\(uc1)?\\pard[^}]*?([^\\]+?)(?=\\rtf1|$)'

            # Try to find text content between RTF tags
            text_patterns = [
                rb'\\pard[^}]*?([^\\\r\n]{10,})',  # Paragraph text
                rb'\\f0\\fs\d+\s+([^\\\r\n]{5,})',  # Formatted text
                rb'([A-Za-z0-9][^\\\r\n]{20,})',     # Plain text blocks
            ]

            note_id = 1
            found_texts = set()  # Avoid duplicates

            # Method 1: Look for readable text sequences
            for match in re.finditer(rb'[\x20-\x7E\s]{30,}', content):
                text_bytes = match.group(0)
                try:
                    text = text_bytes.decode('utf-8', errors='ignore').strip()
                    # Clean RTF tags
                    text = re.sub(r'\\[a-z]+\d*\s*', '', text)
                    text = re.sub(r'[{}\\]', '', text)
                    text = re.sub(r'\s+', ' ', text).strip()

                    # Filter out too short or RTF metadata
                    if (len(text) > 20 and
                        text not in found_texts and
                        not text.startswith(('rtf', 'fonttbl', 'colortbl', 'Microsoft')) and
                        any(c.isalpha() for c in text)):

                        found_texts.add(text)
                        notes.append({
                            'id': f'classic_{note_id}',
                            'content': text,
                            'created_date': 'Unknown',
                            'updated_date': 'Unknown',
                            'theme': 'Classic',
                            'type': 'ClassicNote'
                        })
                        note_id += 1
                except:
                    continue

            # Method 2: Try Unicode (UTF-16) extraction
            for match in re.finditer(rb'(?:[\x20-\x7E]\x00){20,}', content):
                text_bytes = match.group(0)
                try:
                    text = text_bytes.decode('utf-16-le', errors='ignore').strip()
                    text = re.sub(r'[^\x20-\x7E\s]', '', text)
                    text = re.sub(r'\s+', ' ', text).strip()

                    if (len(text) > 20 and
                        text not in found_texts and
                        any(c.isalpha() for c in text)):

                        found_texts.add(text)
                        notes.append({
                            'id': f'classic_{note_id}',
                            'content': text,
                            'created_date': 'Unknown',
                            'updated_date': 'Unknown',
                            'theme': 'Classic',
                            'type': 'ClassicNote'
                        })
                        note_id += 1
                except:
                    continue

            # If no notes found, try simpler extraction
            if not notes:
                # Look for any substantial text content
                text_content = content.decode('latin-1', errors='ignore')
                # Remove RTF codes
                text_content = re.sub(r'\\[a-z]+\d*\s*', '', text_content)
                text_content = re.sub(r'[{}]', '\n', text_content)

                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                for line in lines:
                    if (len(line) > 20 and
                        line not in found_texts and
                        not line.startswith(('rtf', 'fonttbl')) and
                        sum(c.isalpha() for c in line) > 10):

                        found_texts.add(line)
                        notes.append({
                            'id': f'classic_{note_id}',
                            'content': line,
                            'created_date': 'Unknown',
                            'updated_date': 'Unknown',
                            'theme': 'Classic',
                            'type': 'ClassicNote'
                        })
                        note_id += 1

        except Exception as e:
            print(f"Error parsing .snt file: {e}")
            # Return a helpful message
            notes.append({
                'id': 'error_1',
                'content': f'Could not parse classic .snt file. Error: {str(e)}. This format may require manual conversion.',
                'created_date': 'Unknown',
                'updated_date': 'Unknown',
                'theme': 'Error',
                'type': 'ErrorNote'
            })

        return notes


class StickyNotesDatabase:
    """Handle Microsoft Sticky Notes database operations"""
    
    def __init__(self):
        self.db_path = None
        self.connection = None
        
    def find_database(self) -> Optional[str]:
        """
        Automatically detect Microsoft Sticky Notes database
        Supports both modern (plum.sqlite) and classic versions
        """
        system = platform.system().lower()
        possible_paths = []
        
        if system == "windows":
            # Modern Sticky Notes (Windows 10/11)
            user_profile = os.environ.get('USERPROFILE', '')
            modern_paths = [
                os.path.join(user_profile, 'AppData', 'Local', 'Packages', 
                           'Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe', 
                           'LocalState', 'plum.sqlite'),
                # Alternative path for some Windows versions
                os.path.join(user_profile, 'AppData', 'Local', 'Packages',
                           'Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe',
                           'LocalState', 'Legacy', 'ThresholdNotes.snt'),
            ]
            possible_paths.extend(modern_paths)
            
            # Classic Sticky Notes (Windows 7/8/early 10)
            classic_paths = [
                os.path.join(user_profile, 'AppData', 'Roaming', 'Microsoft', 
                           'Sticky Notes', 'StickyNotes.snt'),
                os.path.join(user_profile, 'Documents', 'StickyNotes.snt'),
            ]
            possible_paths.extend(classic_paths)
            
        # Check current directory for manually placed databases
        current_dir_paths = [
            'plum.sqlite',
            'StickyNotes.snt',
            'ThresholdNotes.snt',
        ]
        possible_paths.extend(current_dir_paths)
        
        # Find the first existing database
        for path in possible_paths:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                print(f"Found database: {path}")
                return path
                
        return None
    
    def connect(self, db_path: Optional[str] = None) -> bool:
        """Connect to the database"""
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = self.find_database()

        if not self.db_path:
            return False

        # Check if it's an .snt file (classic format)
        if self.db_path.endswith('.snt'):
            # For .snt files, we don't need a SQL connection
            # Just verify the file exists
            if os.path.exists(self.db_path):
                return True
            else:
                print(f"File not found: {self.db_path}")
                return False
        else:
            # For SQLite databases
            try:
                self.connection = sqlite3.connect(self.db_path)
                return True
            except sqlite3.Error as e:
                print(f"Error connecting to database: {e}")
                return False
    
    def get_table_info(self) -> Dict[str, List[str]]:
        """Get information about available tables and columns"""
        if not self.connection:
            return {}
            
        cursor = self.connection.cursor()
        tables = {}
        
        try:
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [row[0] for row in cursor.fetchall()]
            
            # Get columns for each table
            for table in table_names:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                tables[table] = columns
                
        except sqlite3.Error as e:
            print(f"Error getting table info: {e}")
            
        return tables
    
    def extract_notes(self) -> List[Dict[str, Any]]:
        """Extract all notes from the database"""
        # Check if it's a classic .snt file
        if self.db_path and self.db_path.endswith('.snt'):
            print(f"Parsing classic Sticky Notes file: {self.db_path}")
            return ClassicStickyNotesParser.extract_notes_from_snt(self.db_path)

        # For SQLite databases
        if not self.connection:
            return []

        cursor = self.connection.cursor()
        notes = []

        try:
            # Check if Note table exists (modern format)
            tables = self.get_table_info()
            
            if 'Note' in tables:
                # Modern Sticky Notes format
                query = '''
                    SELECT Id, Text, CreatedAt, UpdatedAt, Theme, Type 
                    FROM Note 
                    WHERE DeletedAt IS NULL 
                    ORDER BY CreatedAt DESC
                '''
                cursor.execute(query)
                
                for row in cursor.fetchall():
                    note_id, text, created_at, updated_at, theme, note_type = row
                    
                    if text:
                        # Clean the text by removing ID prefixes
                        import re
                        clean_text = re.sub(r'\\id=[\w\-_]+\s*', '', text).strip()
                        
                        # Convert Windows file time to readable date
                        try:
                            if created_at:
                                unix_timestamp = (created_at - 116444736000000000) / 10000000
                                created_date = datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                created_date = 'Unknown'
                        except:
                            created_date = str(created_at) if created_at else 'Unknown'
                            
                        try:
                            if updated_at:
                                unix_timestamp = (updated_at - 116444736000000000) / 10000000
                                updated_date = datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                updated_date = created_date
                        except:
                            updated_date = str(updated_at) if updated_at else created_date
                        
                        notes.append({
                            'id': note_id or 'Unknown',
                            'content': clean_text,
                            'created_date': created_date,
                            'updated_date': updated_date,
                            'theme': theme or 'Default',
                            'type': note_type or 'Note'
                        })
            
            # Note: Classic .snt format is handled separately above
                        
        except sqlite3.Error as e:
            print(f"Error extracting notes: {e}")
            
        return notes
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
        # For .snt files, no connection to close
        self.db_path = None