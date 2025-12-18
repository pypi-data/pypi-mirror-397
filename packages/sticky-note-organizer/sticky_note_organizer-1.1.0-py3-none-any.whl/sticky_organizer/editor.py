"""
Note editing, merging, and management functionality
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class NoteEditor:
    """Edit, merge, and manage sticky notes in the database"""

    def __init__(self, db_path: str):
        """
        Initialize note editor

        Args:
            db_path: Path to the sticky notes database
        """
        self.db_path = db_path
        self.connection = None

    def connect(self) -> bool:
        """
        Connect to the database

        Returns:
            True if connection successful
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def update_note(self, note_id: str, new_content: str) -> bool:
        """
        Update the content of a note

        Args:
            note_id: ID of the note to update
            new_content: New content for the note

        Returns:
            True if update was successful

        Raises:
            sqlite3.Error: If database operation fails
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        try:
            cursor = self.connection.cursor()

            # Update the note content and modified date
            # Note: The actual column names might vary, adjust as needed
            cursor.execute("""
                UPDATE Note
                SET Text = ?,
                    UpdatedAt = ?
                WHERE Id = ?
            """, (new_content, datetime.now().isoformat(), note_id))

            self.connection.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Failed to update note: {e}")

    def delete_note(self, note_id: str, permanent: bool = False) -> bool:
        """
        Delete a note from the database

        Args:
            note_id: ID of the note to delete
            permanent: If True, permanently delete; if False, mark as deleted

        Returns:
            True if deletion was successful

        Raises:
            sqlite3.Error: If database operation fails
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        try:
            cursor = self.connection.cursor()

            if permanent:
                # Permanently delete the note
                cursor.execute("DELETE FROM Note WHERE Id = ?", (note_id,))
            else:
                # Mark as deleted (soft delete)
                cursor.execute("""
                    UPDATE Note
                    SET DeletedAt = ?
                    WHERE Id = ?
                """, (datetime.now().isoformat(), note_id))

            self.connection.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Failed to delete note: {e}")

    def merge_notes(self, note_ids: List[str], separator: str = "\n\n---\n\n",
                   keep_first: bool = True) -> Optional[str]:
        """
        Merge multiple notes into a single note

        Args:
            note_ids: List of note IDs to merge
            separator: String to use between merged contents
            keep_first: If True, keep first note and delete others;
                       if False, create new note

        Returns:
            ID of the merged note, or None if merge failed

        Raises:
            sqlite3.Error: If database operation fails
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        if len(note_ids) < 2:
            raise ValueError("Need at least 2 notes to merge")

        try:
            cursor = self.connection.cursor()

            # Fetch all notes to merge
            placeholders = ','.join('?' * len(note_ids))
            cursor.execute(f"""
                SELECT Id, Text, CreatedAt, Theme, WindowPosition
                FROM Note
                WHERE Id IN ({placeholders})
                ORDER BY CreatedAt
            """, note_ids)

            notes = cursor.fetchall()

            if not notes:
                return None

            # Combine content
            merged_content = separator.join(note[1] for note in notes if note[1])

            if keep_first:
                # Update the first note with merged content
                merged_id = notes[0][0]
                cursor.execute("""
                    UPDATE Note
                    SET Text = ?,
                        UpdatedAt = ?
                    WHERE Id = ?
                """, (merged_content, datetime.now().isoformat(), merged_id))

                # Delete the other notes
                for note in notes[1:]:
                    cursor.execute("DELETE FROM Note WHERE Id = ?", (note[0],))

            else:
                # Create a new note with merged content
                import uuid
                merged_id = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO Note (Id, Text, Theme, CreatedAt, UpdatedAt, WindowPosition)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    merged_id,
                    merged_content,
                    notes[0][3],  # Use theme from first note
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    notes[0][4]   # Use position from first note
                ))

                # Delete original notes
                for note in notes:
                    cursor.execute("DELETE FROM Note WHERE Id = ?", (note[0],))

            self.connection.commit()
            return merged_id

        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Failed to merge notes: {e}")

    def bulk_update_category(self, note_ids: List[str], category: str) -> int:
        """
        Update category for multiple notes
        Note: This adds a custom field - may need schema modification

        Args:
            note_ids: List of note IDs to update
            category: New category to assign

        Returns:
            Number of notes updated
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        # Note: The sticky notes database might not have a category field
        # This is a placeholder for future enhancement
        # You might need to use a separate table to store categories

        # For now, we could add it to a custom metadata table
        try:
            cursor = self.connection.cursor()

            # Create metadata table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS NoteMetadata (
                    NoteId TEXT PRIMARY KEY,
                    Category TEXT,
                    Tags TEXT,
                    CustomData TEXT
                )
            """)

            # Update or insert category for each note
            updated = 0
            for note_id in note_ids:
                cursor.execute("""
                    INSERT OR REPLACE INTO NoteMetadata (NoteId, Category)
                    VALUES (?, ?)
                """, (note_id, category))
                updated += cursor.rowcount

            self.connection.commit()
            return updated

        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Failed to update categories: {e}")

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a note by its ID

        Args:
            note_id: ID of the note to retrieve

        Returns:
            Dictionary with note data, or None if not found
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT Id, Text, Theme, CreatedAt, UpdatedAt, DeletedAt
                FROM Note
                WHERE Id = ?
            """, (note_id,))

            row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    'content': row[1],
                    'theme': row[2],
                    'created_date': row[3],
                    'updated_date': row[4],
                    'deleted_date': row[5]
                }

            return None

        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve note: {e}")

    def duplicate_note(self, note_id: str) -> Optional[str]:
        """
        Create a duplicate of a note

        Args:
            note_id: ID of the note to duplicate

        Returns:
            ID of the new duplicated note, or None if failed
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        try:
            cursor = self.connection.cursor()

            # Get original note
            cursor.execute("""
                SELECT Text, Theme, WindowPosition
                FROM Note
                WHERE Id = ?
            """, (note_id,))

            row = cursor.fetchone()

            if not row:
                return None

            # Create new note with same content
            import uuid
            new_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO Note (Id, Text, Theme, CreatedAt, UpdatedAt, WindowPosition)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                new_id,
                row[0] + "\n\n[Copy]",  # Add indicator that this is a copy
                row[1],
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                row[2]
            ))

            self.connection.commit()
            return new_id

        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Failed to duplicate note: {e}")

    def search_and_replace(self, search_text: str, replace_text: str,
                          case_sensitive: bool = False,
                          note_ids: Optional[List[str]] = None) -> int:
        """
        Search and replace text across notes

        Args:
            search_text: Text to search for
            replace_text: Text to replace with
            case_sensitive: Whether search should be case-sensitive
            note_ids: Optional list of specific note IDs to search in

        Returns:
            Number of notes modified
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")

        try:
            cursor = self.connection.cursor()

            # Build query based on parameters
            if note_ids:
                placeholders = ','.join('?' * len(note_ids))
                query = f"SELECT Id, Text FROM Note WHERE Id IN ({placeholders})"
                cursor.execute(query, note_ids)
            else:
                cursor.execute("SELECT Id, Text FROM Note")

            notes = cursor.fetchall()
            modified_count = 0

            for note_id, text in notes:
                if not text:
                    continue

                # Perform replacement
                if case_sensitive:
                    new_text = text.replace(search_text, replace_text)
                else:
                    # Case-insensitive replacement
                    import re
                    pattern = re.compile(re.escape(search_text), re.IGNORECASE)
                    new_text = pattern.sub(replace_text, text)

                # Update if changed
                if new_text != text:
                    cursor.execute("""
                        UPDATE Note
                        SET Text = ?,
                            UpdatedAt = ?
                        WHERE Id = ?
                    """, (new_text, datetime.now().isoformat(), note_id))
                    modified_count += 1

            self.connection.commit()
            return modified_count

        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Failed to search and replace: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
