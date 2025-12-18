"""
Advanced analytics and visualization data generation for sticky notes
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Any
from datetime import datetime, timedelta


class AdvancedAnalytics:
    """Generate advanced analytics and visualization data for sticky notes"""

    def __init__(self):
        """Initialize analytics engine"""
        # Common stop words to filter from word frequency
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
            'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }

    def get_word_frequency(self, notes: List[Dict[str, Any]],
                          top_n: int = 50, min_length: int = 3) -> List[Tuple[str, int]]:
        """
        Get most frequent words across all notes

        Args:
            notes: List of note dictionaries
            top_n: Number of top words to return
            min_length: Minimum word length to consider

        Returns:
            List of (word, count) tuples, sorted by frequency
        """
        word_counter = Counter()

        for note in notes:
            content = note.get('content', '')
            if not content:
                continue

            # Extract words (alphanumeric only)
            words = re.findall(r'\b[a-zA-Z]+\b', content.lower())

            # Filter out stop words and short words
            words = [w for w in words
                    if w not in self.stop_words and len(w) >= min_length]

            word_counter.update(words)

        return word_counter.most_common(top_n)

    def generate_word_cloud_data(self, notes: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Generate word frequency data suitable for word cloud visualization

        Args:
            notes: List of note dictionaries

        Returns:
            Dictionary mapping words to their frequencies
        """
        word_freq = self.get_word_frequency(notes, top_n=100, min_length=4)
        return dict(word_freq)

    def category_distribution(self, categorized_notes: Dict[str, List[Dict]]) -> Dict[str, int]:
        """
        Get count of notes per category

        Args:
            categorized_notes: Dictionary mapping categories to note lists

        Returns:
            Dictionary mapping category names to note counts
        """
        return {category: len(notes) for category, notes in categorized_notes.items()}

    def theme_usage_stats(self, notes: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get statistics on sticky note theme/color usage

        Args:
            notes: List of note dictionaries

        Returns:
            Dictionary mapping themes to usage counts
        """
        theme_counter = Counter()

        for note in notes:
            theme = note.get('theme', 'Unknown')
            theme_counter[theme] += 1

        return dict(theme_counter)

    def timeline_analysis(self, notes: List[Dict[str, Any]],
                         interval: str = 'month') -> Dict[str, int]:
        """
        Analyze note creation over time

        Args:
            notes: List of note dictionaries
            interval: Time interval ('day', 'week', 'month', 'year')

        Returns:
            Dictionary mapping time periods to note counts
        """
        timeline = defaultdict(int)

        for note in notes:
            date_str = note.get('created_date', '')
            if not date_str or date_str == 'Unknown':
                continue

            try:
                # Try to parse as datetime
                if isinstance(date_str, str):
                    # Handle different date formats
                    if len(date_str) > 10:  # Has time component
                        date = datetime.fromisoformat(date_str.replace('T', ' ').split('.')[0])
                    else:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                else:
                    # Might be a timestamp
                    continue

                # Format based on interval
                if interval == 'day':
                    key = date.strftime('%Y-%m-%d')
                elif interval == 'week':
                    key = f"{date.year}-W{date.isocalendar()[1]:02d}"
                elif interval == 'month':
                    key = date.strftime('%Y-%m')
                elif interval == 'year':
                    key = str(date.year)
                else:
                    key = date.strftime('%Y-%m-%d')

                timeline[key] += 1

            except (ValueError, AttributeError):
                continue

        return dict(sorted(timeline.items()))

    def get_category_stats(self, categorized_notes: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Get detailed statistics for each category

        Args:
            categorized_notes: Dictionary mapping categories to note lists

        Returns:
            Dictionary with detailed stats per category
        """
        stats = {}

        for category, notes in categorized_notes.items():
            if not notes:
                continue

            # Calculate various statistics
            total_notes = len(notes)
            total_chars = sum(len(note.get('content', '')) for note in notes)
            avg_length = total_chars / total_notes if total_notes > 0 else 0

            # Get date range
            dates = []
            for note in notes:
                date_str = note.get('created_date', '')
                if date_str and date_str != 'Unknown':
                    try:
                        if isinstance(date_str, str) and len(date_str) > 10:
                            date = datetime.fromisoformat(date_str.replace('T', ' ').split('.')[0])
                            dates.append(date)
                    except:
                        pass

            date_range = None
            if dates:
                date_range = {
                    'earliest': min(dates),
                    'latest': max(dates),
                    'span_days': (max(dates) - min(dates)).days
                }

            stats[category] = {
                'count': total_notes,
                'total_characters': total_chars,
                'avg_length': avg_length,
                'date_range': date_range,
                'percentage': 0  # Will be filled later
            }

        # Calculate percentages
        total_notes = sum(s['count'] for s in stats.values())
        for category in stats:
            stats[category]['percentage'] = (stats[category]['count'] / total_notes * 100)

        return stats

    def top_keywords_by_category(self, categorized_notes: Dict[str, List[Dict]],
                                 top_n: int = 10) -> Dict[str, List[Tuple[str, int]]]:
        """
        Get top keywords for each category

        Args:
            categorized_notes: Dictionary mapping categories to note lists
            top_n: Number of top keywords per category

        Returns:
            Dictionary mapping categories to their top keywords
        """
        category_keywords = {}

        for category, notes in categorized_notes.items():
            keywords = self.get_word_frequency(notes, top_n=top_n)
            category_keywords[category] = keywords

        return category_keywords

    def get_content_length_distribution(self, notes: List[Dict[str, Any]],
                                       buckets: List[int] = None) -> Dict[str, int]:
        """
        Get distribution of note content lengths

        Args:
            notes: List of note dictionaries
            buckets: List of bucket boundaries (e.g., [0, 50, 100, 500, 1000])

        Returns:
            Dictionary mapping length ranges to counts
        """
        if buckets is None:
            buckets = [0, 50, 100, 200, 500, 1000, 5000]

        distribution = defaultdict(int)

        for note in notes:
            content_length = len(note.get('content', ''))

            # Find appropriate bucket
            bucket_label = None
            for i in range(len(buckets) - 1):
                if buckets[i] <= content_length < buckets[i + 1]:
                    bucket_label = f"{buckets[i]}-{buckets[i+1]}"
                    break

            if bucket_label is None and content_length >= buckets[-1]:
                bucket_label = f"{buckets[-1]}+"

            if bucket_label:
                distribution[bucket_label] += 1

        return dict(distribution)

    def find_similar_notes(self, notes: List[Dict[str, Any]],
                          threshold: float = 0.8) -> List[Tuple[Dict, Dict, float]]:
        """
        Find pairs of similar notes (potential duplicates)

        Args:
            notes: List of note dictionaries
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            List of (note1, note2, similarity_score) tuples
        """
        similar_pairs = []

        for i, note1 in enumerate(notes):
            for note2 in notes[i + 1:]:
                similarity = self._calculate_similarity(
                    note1.get('content', ''),
                    note2.get('content', '')
                )

                if similarity >= threshold:
                    similar_pairs.append((note1, note2, similarity))

        # Sort by similarity score, highest first
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        return similar_pairs

    def get_activity_heatmap_data(self, notes: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Generate data for a weekly activity heatmap

        Args:
            notes: List of note dictionaries

        Returns:
            Dictionary mapping weekday-hour combinations to note counts
        """
        heatmap = defaultdict(int)

        for note in notes:
            date_str = note.get('created_date', '')
            if not date_str or date_str == 'Unknown':
                continue

            try:
                if isinstance(date_str, str) and len(date_str) > 10:
                    date = datetime.fromisoformat(date_str.replace('T', ' ').split('.')[0])
                    weekday = date.strftime('%A')
                    hour = date.hour
                    key = f"{weekday}-{hour:02d}"
                    heatmap[key] += 1
            except:
                continue

        return dict(heatmap)

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using Jaccard similarity

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not text1 or not text2:
            return 0.0

        # Convert to lowercase and split into words
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity: intersection / union
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0
