"""
Helper Utility Functions
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import structlog

logger = structlog.get_logger()

def generate_hash(data: Union[str, Dict, List]) -> str:
    """Generate hash for data"""
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode()).hexdigest()

def format_timestamp(timestamp: Any) -> str:
    """Format timestamp to ISO string"""
    if isinstance(timestamp, datetime):
        return timestamp.isoformat()
    elif hasattr(timestamp, 'isoformat'):
        return timestamp.isoformat()
    else:
        return str(timestamp)

def calculate_age(birth_date: Union[str, datetime]) -> int:
    """Calculate age from birth date"""
    try:
        if isinstance(birth_date, str):
            birth_date = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
        
        today = datetime.utcnow()
        age = today.year - birth_date.year
        
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        
        return age
    except Exception as e:
        logger.error("Age calculation failed", error=str(e))
        return 0

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    import re
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not isinstance(text, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = text.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries, with dict2 taking precedence"""
    result = dict1.copy()
    result.update(dict2)
    return result

def filter_none_values(data: Dict) -> Dict:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (part / total) * 100

def round_to_decimals(value: float, decimals: int = 2) -> float:
    """Round value to specified decimal places"""
    return round(value, decimals)

def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID"""
    import uuid
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def generate_random_string(length: int = 8) -> str:
    """Generate random string of specified length"""
    import string
    import random
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def parse_date_range(date_range: str) -> tuple[datetime, datetime]:
    """Parse date range string and return start and end dates"""
    try:
        if date_range == "today":
            today = datetime.utcnow().date()
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
        elif date_range == "week":
            today = datetime.utcnow().date()
            start = datetime.combine(today - timedelta(days=7), datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
        elif date_range == "month":
            today = datetime.utcnow().date()
            start = datetime.combine(today - timedelta(days=30), datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
        else:
            # Default to last 7 days
            today = datetime.utcnow().date()
            start = datetime.combine(today - timedelta(days=7), datetime.min.time())
            end = datetime.combine(today, datetime.max.time())
        
        return start, end
    except Exception as e:
        logger.error("Date range parsing failed", error=str(e))
        # Return default range
        today = datetime.utcnow().date()
        start = datetime.combine(today - timedelta(days=7), datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        return start, end

def validate_dosha_scores(scores: Dict[str, float]) -> bool:
    """Validate dosha scores (should sum to 1.0)"""
    if not isinstance(scores, dict):
        return False
    
    total = sum(scores.values())
    return abs(total - 1.0) < 0.01  # Allow small floating point errors

def normalize_dosha_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Normalize dosha scores to sum to 1.0"""
    total = sum(scores.values())
    if total == 0:
        return {k: 1.0/len(scores) for k in scores.keys()}
    
    return {k: v/total for k, v in scores.items()}

def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI"""
    if height_m <= 0:
        return 0.0
    return weight_kg / (height_m ** 2)

def get_bmi_category(bmi: float) -> str:
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def validate_meal_timing(timing: str) -> bool:
    """Validate meal timing format"""
    valid_timings = ["breakfast", "lunch", "dinner", "snack", "morning", "afternoon", "evening"]
    return timing.lower() in valid_timings

def format_meal_timing(timing: str) -> str:
    """Format meal timing to standard format"""
    timing_map = {
        "morning": "breakfast",
        "afternoon": "lunch",
        "evening": "dinner"
    }
    return timing_map.get(timing.lower(), timing.lower())
