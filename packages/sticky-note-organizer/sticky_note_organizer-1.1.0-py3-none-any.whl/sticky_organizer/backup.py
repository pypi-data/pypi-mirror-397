"""
Backup and restore functionality for sticky notes database
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class BackupManager:
    """Manage backup and restore operations for sticky notes database"""

    def __init__(self, backup_dir: str = "backups"):
        """
        Initialize backup manager

        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, db_path: str, compress: bool = True,
                     custom_name: Optional[str] = None) -> str:
        """
        Create a backup of the database

        Args:
            db_path: Path to the database file
            compress: Whether to compress the backup (ZIP format)
            custom_name: Custom name for backup (default: auto-generated timestamp)

        Returns:
            Path to the created backup file

        Raises:
            FileNotFoundError: If database file doesn't exist
            IOError: If backup creation fails
        """
        db_path = Path(db_path)

        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_name:
            backup_name = f"{custom_name}_{timestamp}"
        else:
            backup_name = f"sticky_notes_backup_{timestamp}"

        if compress:
            backup_file = self.backup_dir / f"{backup_name}.zip"

            # Create ZIP archive
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(db_path, db_path.name)

                # Add metadata file
                metadata = self._generate_metadata(db_path)
                zipf.writestr('backup_info.txt', metadata)
        else:
            backup_file = self.backup_dir / f"{backup_name}.sqlite"
            shutil.copy2(db_path, backup_file)

        return str(backup_file)

    def restore_backup(self, backup_path: str, target_path: str,
                      create_backup_first: bool = True) -> bool:
        """
        Restore database from a backup

        Args:
            backup_path: Path to the backup file
            target_path: Path where to restore the database
            create_backup_first: Create backup of current database before restoring

        Returns:
            True if restoration was successful

        Raises:
            FileNotFoundError: If backup file doesn't exist
            IOError: If restoration fails
        """
        backup_path = Path(backup_path)
        target_path = Path(target_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Create backup of current database if it exists and requested
        if create_backup_first and target_path.exists():
            self.create_backup(str(target_path), custom_name="pre_restore")

        # Restore from ZIP or direct copy
        if backup_path.suffix == '.zip':
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Find the database file in the archive
                db_files = [f for f in zipf.namelist()
                           if f.endswith('.sqlite') or f.endswith('.snt')]

                if not db_files:
                    raise ValueError("No database file found in backup archive")

                # Extract the first database file
                zipf.extract(db_files[0], target_path.parent)

                # Rename to target path if necessary
                extracted_path = target_path.parent / db_files[0]
                if extracted_path != target_path:
                    shutil.move(str(extracted_path), str(target_path))
        else:
            shutil.copy2(backup_path, target_path)

        return True

    def list_backups(self) -> List[Dict[str, any]]:
        """
        List all available backups

        Returns:
            List of dictionaries containing backup information:
            - name: Backup filename
            - path: Full path to backup
            - size: File size in bytes
            - created: Creation timestamp
            - compressed: Whether backup is compressed
        """
        backups = []

        for backup_file in self.backup_dir.iterdir():
            if backup_file.is_file() and (backup_file.suffix in ['.zip', '.sqlite', '.snt']):
                stat = backup_file.stat()

                # Try to parse timestamp from filename
                created = datetime.fromtimestamp(stat.st_mtime)

                backups.append({
                    'name': backup_file.name,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'created': created,
                    'compressed': backup_file.suffix == '.zip'
                })

        # Sort by creation time, newest first
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups

    def delete_backup(self, backup_path: str) -> bool:
        """
        Delete a backup file

        Args:
            backup_path: Path to the backup file to delete

        Returns:
            True if deletion was successful
        """
        backup_path = Path(backup_path)

        if backup_path.exists():
            backup_path.unlink()
            return True

        return False

    def auto_backup(self, db_path: str, keep_last_n: int = 10) -> str:
        """
        Create an automatic backup and clean up old backups

        Args:
            db_path: Path to the database file
            keep_last_n: Number of most recent backups to keep

        Returns:
            Path to the created backup file
        """
        # Create new backup
        backup_file = self.create_backup(db_path, custom_name="auto")

        # Clean up old auto backups
        auto_backups = [b for b in self.list_backups() if 'auto' in b['name']]

        if len(auto_backups) > keep_last_n:
            # Delete oldest backups beyond keep_last_n
            for backup in auto_backups[keep_last_n:]:
                self.delete_backup(backup['path'])

        return backup_file

    def get_backup_info(self, backup_path: str) -> Optional[Dict[str, any]]:
        """
        Get detailed information about a backup

        Args:
            backup_path: Path to the backup file

        Returns:
            Dictionary with backup details or None if not found
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            return None

        info = {
            'name': backup_path.name,
            'path': str(backup_path),
            'size': backup_path.stat().st_size,
            'created': datetime.fromtimestamp(backup_path.stat().st_mtime),
            'compressed': backup_path.suffix == '.zip'
        }

        # If ZIP, read metadata
        if info['compressed']:
            try:
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    if 'backup_info.txt' in zipf.namelist():
                        info['metadata'] = zipf.read('backup_info.txt').decode('utf-8')
            except:
                pass

        return info

    def _generate_metadata(self, db_path: Path) -> str:
        """Generate metadata text for backup"""
        stat = db_path.stat()

        metadata = f"""Sticky Notes Database Backup
================================
Original file: {db_path.name}
Original size: {stat.st_size:,} bytes
Backup created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Original modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}

This backup was created by Sticky Note Organizer.
To restore, use: sticky-organizer restore <backup_file>
"""
        return metadata

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
