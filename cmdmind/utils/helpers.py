"""
Helper utilities for CmdMind
"""

import re
from datetime import datetime
from typing import List, Tuple, Optional


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate a string to a maximum length"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def format_timestamp(dt: datetime, format_type: str = "default") -> str:
    """Format a timestamp for display"""
    if format_type == "default":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "short":
        return dt.strftime("%m/%d %H:%M")
    elif format_type == "relative":
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 7:
            return dt.strftime("%Y-%m-%d")
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "just now"
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_command_args(command: str) -> Tuple[str, List[str]]:
    """Parse a command into program and arguments"""
    # Handle quoted strings
    parts = re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', command)
    
    if not parts:
        return ("", [])
    
    program = parts[0].strip('"')
    args = [arg.strip('"') for arg in parts[1:]]
    
    return (program, args)


def is_valid_command(command: str) -> bool:
    """Check if a command string is valid"""
    if not command or not command.strip():
        return False
    
    # Check for basic shell syntax issues
    # Unmatched quotes
    single_quotes = command.count("'") - command.count("\\'")
    double_quotes = command.count('"') - command.count('\\"')
    
    if single_quotes % 2 != 0 or double_quotes % 2 != 0:
        return False
    
    return True


def extract_command_base(command: str) -> str:
    """Extract the base command (first word)"""
    parts = command.strip().split()
    return parts[0] if parts else ""


def sanitize_for_display(command: str) -> str:
    """Sanitize a command for safe display"""
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', command)
    # Truncate very long commands
    if len(sanitized) > 200:
        sanitized = sanitized[:200] + "..."
    return sanitized


def calculate_command_similarity(cmd1: str, cmd2: str) -> float:
    """Calculate similarity between two commands"""
    from rapidfuzz import fuzz
    
    # Normalize commands
    c1 = cmd1.lower().strip()
    c2 = cmd2.lower().strip()
    
    # Use partial ratio for substring matching
    return fuzz.partial_ratio(c1, c2) / 100.0


def get_command_risk_level(command: str) -> str:
    """Assess risk level of a command"""
    dangerous_patterns = [
        r'\brm\s+-rf\b',
        r'\brm\s+-fr\b',
        r'\bdd\s+if=',
        r'\bmkfs\b',
        r'\bformat\b',
        r'\b>\s*/dev/',
        r'\bchmod\s+777\b',
        r'\bchown\s+.*:.*\s+/',
        r'\bshutdown\b',
        r'\breboot\b',
        r'\binit\s+0\b',
        r'\binit\s+6\b',
    ]
    
    command_lower = command.lower()
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command_lower):
            return "high"
    
    # Check for sudo
    if 'sudo' in command_lower:
        return "medium"
    
    return "low"
