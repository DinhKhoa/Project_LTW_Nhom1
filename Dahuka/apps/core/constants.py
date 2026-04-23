"""
Application-wide constants.
Centralized location for all magic numbers, configuration values, and constants
to avoid hardcoding values throughout the codebase.
"""

# Pagination
DEFAULT_PAGE_SIZE = 10
ADMIN_PAGE_SIZE = 10

# Cart & Orders
CART_DEFAULT_DEPOSIT_PERCENT = 10
CART_MIN_DEPOSIT_PERCENT = 10
CART_MAX_DEPOSIT_PERCENT = 50
DEFAULT_DELIVERY_CITY = "Đà Nẵng"
DEFAULT_DELIVERY_DAYS = 3

# Phone number format
PHONE_FORMAT_REGEX = r'^[0-9]{10,11}$'
PHONE_MIN_LENGTH = 10
PHONE_MAX_LENGTH = 11
