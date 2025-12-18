"""
Export functionality for different output formats
"""

import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class BaseExporter:
    """Base class for all exporters"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export(self, notes: List[Dict[str, Any]], filename: str) -> str:
        """Export notes to file"""
        raise NotImplementedError


class CSVExporter(BaseExporter):
    """Export notes to CSV format"""
    
    def export(self, notes: List[Dict[str, Any]], filename: str = "sticky_notes") -> str:
        """Export to CSV file"""
        filepath = self.output_dir / f"{filename}.csv"
        
        if not notes:
            return str(filepath)
        
        fieldnames = list(notes[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(notes)
        
        return str(filepath)


class JSONExporter(BaseExporter):
    """Export notes to JSON format"""
    
    def export(self, notes: List[Dict[str, Any]], filename: str = "sticky_notes") -> str:
        """Export to JSON file"""
        filepath = self.output_dir / f"{filename}.json"
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_notes": len(notes),
            "notes": notes
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        return str(filepath)


class ExcelExporter(BaseExporter):
    """Export notes to Excel format"""
    
    def export(self, notes: List[Dict[str, Any]], filename: str = "sticky_notes") -> str:
        """Export to Excel file"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas and openpyxl are required for Excel export")
        
        filepath = self.output_dir / f"{filename}.xlsx"
        
        if not notes:
            return str(filepath)
        
        df = pd.DataFrame(notes)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main sheet with all notes
            df.to_excel(writer, sheet_name='All Notes', index=False)
            
            # Separate sheets by category if category column exists
            if 'category' in df.columns:
                for category in df['category'].unique():
                    category_df = df[df['category'] == category]
                    # Excel sheet names have character limits and invalid characters
                    sheet_name = str(category)[:30].replace('/', '-')
                    category_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return str(filepath)


class MarkdownExporter(BaseExporter):
    """Export notes to Markdown format"""
    
    def export(self, notes: List[Dict[str, Any]], filename: str = "sticky_notes") -> str:
        """Export to Markdown file"""
        filepath = self.output_dir / f"{filename}.md"
        
        with open(filepath, 'w', encoding='utf-8') as mdfile:
            mdfile.write("# Microsoft Sticky Notes Export\n\n")
            mdfile.write(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            mdfile.write(f"**Total Notes:** {len(notes)}\n\n")
            
            # Group by category if available
            if notes and 'category' in notes[0]:
                categories = {}
                for note in notes:
                    category = note.get('category', 'Uncategorized')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(note)
                
                for category, category_notes in sorted(categories.items()):
                    mdfile.write(f"## {category} ({len(category_notes)} notes)\n\n")
                    
                    for note in category_notes:
                        mdfile.write(f"### Note from {note.get('created_date', 'Unknown')}\n")
                        if note.get('theme'):
                            mdfile.write(f"**Theme:** {note['theme']}\n\n")
                        mdfile.write(f"{note['content']}\n\n")
                        mdfile.write("---\n\n")
            else:
                # Simple format without categories
                for i, note in enumerate(notes, 1):
                    mdfile.write(f"## Note {i}\n")
                    mdfile.write(f"**Date:** {note.get('created_date', 'Unknown')}\n")
                    if note.get('theme'):
                        mdfile.write(f"**Theme:** {note['theme']}\n")
                    mdfile.write(f"\n{note['content']}\n\n")
                    mdfile.write("---\n\n")
        
        return str(filepath)


class SummaryExporter(BaseExporter):
    """Export organized summary"""
    
    def export(self, categorized_notes, filename: str = "notes_summary") -> str:
        """Export summary to text file"""
        filepath = self.output_dir / f"{filename}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as summary_file:
            summary_file.write("MICROSOFT STICKY NOTES SUMMARY\n")
            summary_file.write("=" * 50 + "\n\n")
            
            # Sort categories by number of notes
            sorted_categories = sorted(categorized_notes.items(), 
                                     key=lambda x: len(x[1]), reverse=True)
            
            for category, notes in sorted_categories:
                summary_file.write(f"{category.upper()} ({len(notes)} notes)\n")
                summary_file.write("-" * (len(category) + 10) + "\n\n")
                
                # Show key items from each category
                for note in notes[:10]:  # Show up to 10 items per category
                    content = note['content']
                    if len(content) > 10:
                        summary_file.write(f"• {content[:100]}{'...' if len(content) > 100 else ''}\n")
                
                summary_file.write("\n" + "="*50 + "\n\n")
        
        return str(filepath)


class ExportManager:
    """Manage different export formats"""
    
    def __init__(self, output_dir: str = "output"):
        self.exporters = {
            'csv': CSVExporter(output_dir),
            'json': JSONExporter(output_dir),
            'excel': ExcelExporter(output_dir) if PANDAS_AVAILABLE else None,
            'markdown': MarkdownExporter(output_dir),
            'summary': SummaryExporter(output_dir)
        }
    
    def get_available_formats(self) -> List[str]:
        """Get list of available export formats"""
        return [fmt for fmt, exporter in self.exporters.items() if exporter is not None]
    
    def export(self, notes: List[Dict[str, Any]], formats: List[str], 
              filename: str = "sticky_notes") -> Dict[str, str]:
        """Export notes in multiple formats"""
        results = {}
        
        for fmt in formats:
            if fmt not in self.exporters or self.exporters[fmt] is None:
                results[fmt] = f"Format '{fmt}' not available"
                continue
            
            try:
                filepath = self.exporters[fmt].export(notes, filename)
                results[fmt] = filepath
            except Exception as e:
                results[fmt] = f"Error exporting {fmt}: {str(e)}"
        
        return results
    
    def export_summary(self, categorized_notes: Dict[str, List[Dict[str, Any]]], 
                      filename: str = "notes_summary") -> str:
        """Export summary text file"""
        return self.exporters['summary'].export(categorized_notes, filename)