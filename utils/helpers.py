"""
Utility functions for the application
"""

import logging
from datetime import datetime
from flask_login import current_user

logger = logging.getLogger(__name__)

def log_activity(message, user=None, level='info'):
    """
    Log user activities for audit purposes
    
    Args:
        message (str): Activity message
        user: User object (optional, defaults to current_user)
        level (str): Log level (info, warning, error)
    """
    if user is None and hasattr(current_user, 'id'):
        user = current_user
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_info = f"User {user.id} ({user.username})" if user and hasattr(user, 'id') else "Unknown user"
    
    log_message = f"[{timestamp}] {user_info}: {message}"
    
    if level == 'error':
        logger.error(log_message)
    elif level == 'warning':
        logger.warning(log_message)
    else:
        logger.info(log_message)

def format_currency(amount, currency_symbol='ر.س'):
    """
    Format currency amount for display
    
    Args:
        amount: Numeric amount
        currency_symbol: Currency symbol (default: Saudi Riyal)
    
    Returns:
        str: Formatted currency string
    """
    try:
        amount = float(amount) if amount else 0
        return f"{amount:,.2f} {currency_symbol}"
    except (ValueError, TypeError):
        return f"0.00 {currency_symbol}"

def safe_decimal(value, default=0):
    """
    Safely convert value to decimal with fallback
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
    
    Returns:
        float: Converted value or default
    """
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default