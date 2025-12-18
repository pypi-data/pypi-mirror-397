"""
Advanced filtering and processing features
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable


class NoteFilter:
    """Advanced note filtering functionality"""
    
    def __init__(self):
        self.filters = []
    
    def by_date_range(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> 'NoteFilter':
        """Filter notes by date range"""
        def date_filter(note: Dict[str, Any]) -> bool:
            try:
                note_date = datetime.strptime(note['created_date'], '%Y-%m-%d %H:%M:%S')
                
                if start_date:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    if note_date < start_dt:
                        return False
                
                if end_date:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    # Add one day to include the entire end date
                    end_dt = end_dt + timedelta(days=1)
                    if note_date >= end_dt:
                        return False
                
                return True
            except (ValueError, KeyError):
                return True  # Include notes with invalid dates
        
        self.filters.append(date_filter)
        return self
    
    def by_content_length(self, min_length: Optional[int] = None, max_length: Optional[int] = None) -> 'NoteFilter':
        """Filter notes by content length"""
        def length_filter(note: Dict[str, Any]) -> bool:
            content_length = len(note.get('content', ''))
            
            if min_length is not None and content_length < min_length:
                return False
            
            if max_length is not None and content_length > max_length:
                return False
            
            return True
        
        self.filters.append(length_filter)
        return self
    
    def by_theme(self, themes: List[str]) -> 'NoteFilter':
        """Filter notes by theme/color"""
        def theme_filter(note: Dict[str, Any]) -> bool:
            note_theme = note.get('theme', '').lower()
            return any(theme.lower() in note_theme for theme in themes)
        
        self.filters.append(theme_filter)
        return self
    
    def by_category(self, categories: List[str]) -> 'NoteFilter':
        """Filter notes by category"""
        def category_filter(note: Dict[str, Any]) -> bool:
            note_category = note.get('category', '')
            return note_category in categories
        
        self.filters.append(category_filter)
        return self
    
    def by_regex(self, pattern: str, case_sensitive: bool = False) -> 'NoteFilter':
        """Filter notes by regex pattern"""
        flags = 0 if case_sensitive else re.IGNORECASE
        compiled_pattern = re.compile(pattern, flags)
        
        def regex_filter(note: Dict[str, Any]) -> bool:
            content = note.get('content', '')
            return bool(compiled_pattern.search(content))
        
        self.filters.append(regex_filter)
        return self
    
    def by_keywords(self, keywords: List[str], match_all: bool = False, case_sensitive: bool = False) -> 'NoteFilter':
        """Filter notes by keywords"""
        def keyword_filter(note: Dict[str, Any]) -> bool:
            content = note.get('content', '')
            if not case_sensitive:
                content = content.lower()
                keywords_to_check = [kw.lower() for kw in keywords]
            else:
                keywords_to_check = keywords
            
            if match_all:
                return all(kw in content for kw in keywords_to_check)
            else:
                return any(kw in content for kw in keywords_to_check)
        
        self.filters.append(keyword_filter)
        return self
    
    def by_has_urls(self) -> 'NoteFilter':
        """Filter notes that contain URLs"""
        url_pattern = re.compile(r'https?://[^\s]+', re.IGNORECASE)
        
        def url_filter(note: Dict[str, Any]) -> bool:
            content = note.get('content', '')
            return bool(url_pattern.search(content))
        
        self.filters.append(url_filter)
        return self
    
    def by_has_emails(self) -> 'NoteFilter':
        """Filter notes that contain email addresses"""
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        def email_filter(note: Dict[str, Any]) -> bool:
            content = note.get('content', '')
            return bool(email_pattern.search(content))
        
        self.filters.append(email_filter)
        return self
    
    def by_has_phone_numbers(self) -> 'NoteFilter':
        """Filter notes that contain phone numbers"""
        phone_pattern = re.compile(r'\b\d{10,}\b')
        
        def phone_filter(note: Dict[str, Any]) -> bool:
            content = note.get('content', '')
            return bool(phone_pattern.search(content))
        
        self.filters.append(phone_filter)
        return self
    
    def apply(self, notes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all filters to the notes"""
        filtered_notes = notes
        
        for filter_func in self.filters:
            filtered_notes = [note for note in filtered_notes if filter_func(note)]
        
        return filtered_notes
    
    def reset(self) -> 'NoteFilter':
        """Clear all filters"""
        self.filters = []
        return self


class NoteSorter:
    """Sort notes by different criteria"""
    
    @staticmethod
    def by_date(notes: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
        """Sort notes by creation date"""
        def date_key(note: Dict[str, Any]):
            try:
                return datetime.strptime(note['created_date'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, KeyError):
                return datetime.min if ascending else datetime.max
        
        return sorted(notes, key=date_key, reverse=not ascending)
    
    @staticmethod
    def by_length(notes: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
        """Sort notes by content length"""
        return sorted(notes, key=lambda x: len(x.get('content', '')), reverse=not ascending)
    
    @staticmethod
    def by_category(notes: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
        """Sort notes by category name"""
        return sorted(notes, key=lambda x: x.get('category', ''), reverse=not ascending)
    
    @staticmethod
    def by_theme(notes: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
        """Sort notes by theme"""
        return sorted(notes, key=lambda x: x.get('theme', ''), reverse=not ascending)


class NoteAnalyzer:
    """Analyze note patterns and statistics"""
    
    @staticmethod
    def get_word_frequency(notes: List[Dict[str, Any]], top_n: int = 20) -> List[tuple]:
        """Get most frequent words across all notes"""
        word_count = {}
        
        for note in notes:
            content = note.get('content', '').lower()
            # Remove common punctuation and split into words
            words = re.findall(r'\b[a-z]{3,}\b', content)
            
            for word in words:
                if word not in {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'use', 'way', 'who', 'oil', 'sit', 'set', 'run', 'eat'}:
                    word_count[word] = word_count.get(word, 0) + 1
        
        return sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    @staticmethod
    def get_category_stats(categorized_notes: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each category"""
        stats = {}
        
        for category, notes in categorized_notes.items():
            if not notes:
                continue
                
            contents = [note['content'] for note in notes]
            lengths = [len(content) for content in contents]
            
            stats[category] = {
                'count': len(notes),
                'avg_length': sum(lengths) / len(lengths) if lengths else 0,
                'min_length': min(lengths) if lengths else 0,
                'max_length': max(lengths) if lengths else 0,
                'total_chars': sum(lengths),
            }
            
            # Get creation dates
            dates = []
            for note in notes:
                try:
                    date = datetime.strptime(note['created_date'], '%Y-%m-%d %H:%M:%S')
                    dates.append(date)
                except (ValueError, KeyError):
                    pass
            
            if dates:
                stats[category].update({
                    'oldest': min(dates).strftime('%Y-%m-%d'),
                    'newest': max(dates).strftime('%Y-%m-%d'),
                    'date_span_days': (max(dates) - min(dates)).days
                })
        
        return stats
    
    @staticmethod
    def find_duplicates(notes: List[Dict[str, Any]], similarity_threshold: float = 0.9) -> List[List[Dict[str, Any]]]:
        """Find potentially duplicate notes"""
        duplicates = []
        processed = set()
        
        for i, note1 in enumerate(notes):
            if i in processed:
                continue
                
            similar_group = [note1]
            content1 = note1.get('content', '').lower().strip()
            
            for j, note2 in enumerate(notes[i+1:], i+1):
                if j in processed:
                    continue
                    
                content2 = note2.get('content', '').lower().strip()
                
                # Simple similarity check (can be enhanced with more sophisticated algorithms)
                if content1 == content2:
                    similar_group.append(note2)
                    processed.add(j)
                elif len(content1) > 20 and len(content2) > 20:
                    # Check for substantial overlap
                    shorter = min(content1, content2, key=len)
                    longer = max(content1, content2, key=len)
                    if shorter in longer and len(shorter) / len(longer) > similarity_threshold:
                        similar_group.append(note2)
                        processed.add(j)
            
            if len(similar_group) > 1:
                duplicates.append(similar_group)
                processed.add(i)
        
        return duplicates