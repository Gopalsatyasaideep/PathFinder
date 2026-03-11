"""
Text Cleaning Utilities

This module provides functions to clean and normalize text extracted from resumes.
Removes unnecessary characters, normalizes whitespace, and prepares text for parsing.
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean extracted text from resume files.
    
    Removes:
    - Multiple consecutive whitespaces
    - Special formatting characters
    - Excessive newlines
    - Non-printable characters
    
    Args:
        text: Raw text extracted from resume
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove non-printable characters except newlines and tabs
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
    
    # Normalize whitespace - replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Normalize newlines - replace multiple newlines with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove excessive tabs
    text = re.sub(r'\t+', ' ', text)
    
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Final cleanup - remove any remaining excessive whitespace
    text = text.strip()
    
    return text


def extract_sentences(text: str) -> List[str]:
    """
    Split text into sentences for better parsing.
    
    Uses simple sentence splitting based on punctuation.
    This is heuristic-based and may not be perfect for all cases.
    
    Args:
        text: Cleaned text string
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    # Split on sentence-ending punctuation
    # This is a simple heuristic - spaCy's sentence tokenizer would be better
    # but we're keeping it simple for now
    sentences = re.split(r'[.!?]+\s+', text)
    
    # Filter out empty sentences and very short fragments
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    return sentences


def normalize_skill_name(skill: str) -> str:
    """
    Normalize skill names for consistent matching.
    
    Converts to lowercase, removes extra spaces, handles common variations.
    
    Args:
        skill: Raw skill string
        
    Returns:
        Normalized skill name
    """
    if not skill:
        return ""
    
    # Convert to lowercase and strip
    skill = skill.lower().strip()
    
    # Remove common prefixes/suffixes
    skill = re.sub(r'^(knowledge of|experience with|proficient in|skilled in)\s+', '', skill)
    
    # Remove extra spaces
    skill = re.sub(r'\s+', ' ', skill)
    
    return skill
