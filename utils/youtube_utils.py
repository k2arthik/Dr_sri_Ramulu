"""
YouTube utility functions for extracting video IDs and generating URLs.
"""
import re


def extract_youtube_id(url):
    """
    Extract YouTube video ID from various URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    
    Args:
        url (str): YouTube URL or video ID
        
    Returns:
        str: 11-character video ID or None if invalid
    """
    if not url:
        return None
    
    # If it's already an 11-character alphanumeric string, return it
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url.strip()):
        return url.strip()
    
    # Extract from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/shorts\/|youtube\.com\/v\/|youtube\.com\/\?v=)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_youtube_thumbnail_url(video_id, quality='maxresdefault'):
    """
    Generate YouTube thumbnail URL from video ID.
    
    Args:
        video_id (str): YouTube video ID
        quality (str): Thumbnail quality - 'maxresdefault', 'hqdefault', 'mqdefault', 'sddefault'
        
    Returns:
        str: Thumbnail URL
    """
    if not video_id:
        return None
    
    return f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"


def get_youtube_embed_url(video_id, autoplay=False, rel=False, origin=None):
    """
    Generate YouTube embed URL from video ID.
    
    Args:
        video_id (str): YouTube video ID
        autoplay (bool): Enable autoplay
        rel (bool): Show related videos
        origin (str): Origin domain for security
        
    Returns:
        str: Embed URL
    """
    if not video_id:
        return None
    
    params = []
    
    if not autoplay:
        params.append('autoplay=0')
    else:
        params.append('autoplay=1')
    
    if not rel:
        params.append('rel=0')
    
    params.append('enablejsapi=1')
    
    if origin:
        params.append(f'origin={origin}')
    
    param_string = '&'.join(params)
    return f"https://www.youtube.com/embed/{video_id}?{param_string}"


def validate_youtube_id(video_id):
    """
    Validate that a string is a valid YouTube video ID.
    
    Args:
        video_id (str): String to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not video_id:
        return False
    
    return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))
