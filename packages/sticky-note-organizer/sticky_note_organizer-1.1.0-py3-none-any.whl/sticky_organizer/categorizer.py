"""
Note categorization and organization logic
"""

import re
from collections import defaultdict
from typing import List, Dict, Any


class NoteCategorizer:
    """Categorize and organize notes by themes"""
    
    def __init__(self):
        self.categories = {
            'Business Ideas': [
                'business', 'startup', 'idea', 'company', 'revenue', 'profit', 'market', 'customer',
                'product', 'service', 'venture', 'investment', 'funding', 'monetize', 'scale',
                'opportunity', 'competitor', 'strategy', 'launch', 'pitch', 'entrepreneur',
                'marketing', 'seo', 'content marketing', 'branding', 'positioning'
            ],
            'Financial/Money': [
                'money', 'cash', 'payment', 'debt', 'loan', 'budget', 'expense', 'income',
                'salary', 'cost', 'price', 'financial', 'bank', 'account', 'investment',
                'portfolio', 'savings', '$', '₦', 'naira', 'dollar', 'pay', 'buy', 'sell',
                'mortgage', 'insurance', 'tax', 'crypto', 'bitcoin', 'trading'
            ],
            'Personal Goals': [
                'goal', 'achieve', 'plan', 'target', 'objective', 'dream', 'aspiration',
                'improve', 'learn', 'skill', 'habit', 'routine', 'personal', 'growth',
                'development', 'resolution', 'milestone', 'progress', 'therapy'
            ],
            'Work/Career': [
                'work', 'job', 'career', 'office', 'meeting', 'project', 'task', 'deadline',
                'boss', 'colleague', 'client', 'resume', 'interview', 'promotion',
                'performance', 'team', 'department', 'professional', 'upwork', 'freelance'
            ],
            'Technology/Development': [
                'code', 'programming', 'software', 'app', 'website', 'development', 'tech',
                'computer', 'system', 'database', 'api', 'framework', 'algorithm',
                'python', 'javascript', 'html', 'css', 'server', 'cloud', 'github'
            ],
            'Health/Fitness': [
                'health', 'fitness', 'exercise', 'workout', 'diet', 'nutrition', 'gym',
                'weight', 'doctor', 'medicine', 'wellness', 'mental health', 'stress',
                'sleep', 'energy', 'body', 'mind', 'meditation'
            ],
            'Contacts/People': [
                'contact', 'phone', 'email', 'address', 'friend', 'family', 'colleague',
                'client', 'partner', 'relationship', 'network', 'connection'
            ],
            'Travel/Places': [
                'travel', 'trip', 'vacation', 'flight', 'hotel', 'country', 'city',
                'visit', 'destination', 'location', 'address', 'place', 'journey',
                'passport', 'visa', 'booking'
            ],
            'Shopping/Items': [
                'buy', 'purchase', 'shopping', 'store', 'item', 'product', 'brand',
                'order', 'delivery', 'price', 'discount', 'sale', 'market', 'amazon'
            ],
            'Ideas/Thoughts': [
                'idea', 'thought', 'concept', 'inspiration', 'brainstorm', 'creative',
                'innovation', 'solution', 'approach', 'method', 'strategy', 'innovation'
            ],
            'Tasks/Reminders': [
                'todo', 'task', 'reminder', 'remember', 'do', 'call', 'check',
                'follow up', 'schedule', 'appointment', 'urgent', 'important', 'deadline'
            ],
            'Education/Learning': [
                'learn', 'study', 'course', 'book', 'education', 'knowledge', 'skill',
                'training', 'certification', 'degree', 'school', 'university', 'research'
            ]
        }
    
    def categorize_note(self, content: str) -> str:
        """Categorize a single note based on its content"""
        # Handle None or empty content
        if not content:
            return 'Miscellaneous'

        content_lower = content.lower()
        best_category = 'Miscellaneous'
        max_matches = 0
        
        # Find the category with most keyword matches
        for category, keywords in self.categories.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        # Special rules for better categorization
        if any(char in content_lower for char in ['₦', '$', 'naira', 'dollar']) or \
           any(word in content_lower for word in ['pay', 'money', 'cash', 'debt', 'loan']):
            best_category = 'Financial/Money'

        # If it looks like contact info (has phone numbers or emails)
        # Check this before URL check to prioritize contact detection
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content_lower) or \
           re.search(r'\w+@\w+\.\w+', content_lower):
            best_category = 'Contacts/People'

        # If it's a URL or website (but not if already categorized as contact)
        elif 'http' in content_lower or '.com' in content_lower or '.net' in content_lower:
            if 'business' in content_lower or 'marketing' in content_lower:
                best_category = 'Business Ideas'
            else:
                best_category = 'Technology/Development'
        
        # If it contains code-like patterns
        if re.search(r'function\s*\(|def\s+\w+|class\s+\w+|<\w+>|{\s*\w+:', content_lower):
            best_category = 'Technology/Development'
            
        return best_category
    
    def categorize_notes(self, notes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize all notes and return grouped by category"""
        categorized = defaultdict(list)
        
        for note in notes:
            category = self.categorize_note(note['content'])
            note['category'] = category
            categorized[category].append(note)
        
        return dict(categorized)
    
    def get_category_summary(self, categorized_notes: Dict[str, List[Dict[str, Any]]]) -> Dict[str, int]:
        """Get summary of notes count per category"""
        return {category: len(notes) for category, notes in categorized_notes.items()}
    
    def add_custom_category(self, name: str, keywords: List[str]):
        """Add a custom category with keywords"""
        self.categories[name] = keywords
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get all available categories and their keywords"""
        return self.categories.copy()