"""Helper utility functions for the Mail List Shield application.

This module provides general-purpose helper functions including file size
formatting, code generation, and API key generation.
"""

from random import randrange
import uuid

from app import bc


def readable_file_size(size_in_bytes, significant_digits=0):
    """Convert a file size in bytes to a human-readable string.

    Args:
        size_in_bytes: The size in bytes to convert.
        significant_digits: Number of decimal places to include.

    Returns:
        str: Human-readable size string (e.g., '5 MB', '1.5 GB').
    """
    if size_in_bytes < 1024:
        size_rounded = round(size_in_bytes, significant_digits)
        if significant_digits == 0:
            size_rounded = int(size_rounded)
        result = str(size_rounded) + " B"
    elif size_in_bytes < 1024**2:
        size_rounded = round(size_in_bytes / 1024, significant_digits)
        if significant_digits == 0:
            size_rounded = int(size_rounded)
        result = str(size_rounded) + " KB"
    elif size_in_bytes < 1024**3:
        size_rounded = round(size_in_bytes / 1024 / 1024, significant_digits)
        if significant_digits == 0:
            size_rounded = int(size_rounded)
        result = str(size_rounded) + " MB"
    elif size_in_bytes < 1024**4:
        size_rounded = round(size_in_bytes / 1024 / 1024 / 1024, significant_digits)
        if significant_digits == 0:
            size_rounded = int(size_rounded)
        result = str(size_rounded) + " GB"
    return result


def generate_n_digit_code(n):
    """Generate a random n-digit numeric code.

    Each digit is between 1-9 (no zeros) for better readability.

    Args:
        n: The number of digits in the code.

    Returns:
        str: A string of n random digits.
    """
    code = ""
    for i in range(n):
        code = code + str(randrange(9) + 1)
    return code


def generate_api_key_and_hash():
    """Generate a new API key and its bcrypt hash.

    Creates a 64-character random API key and hashes it for secure storage.

    Returns:
        tuple: A tuple containing (plaintext_key, hashed_key).
            The plaintext key should be shown to the user once,
            while the hash is stored in the database.
    """
    # Generate a new random key
    new_key = uuid.uuid4().hex + uuid.uuid4().hex  # 64 characters

    # Hash the key to be stored in the database
    key_hash = bc.generate_password_hash(new_key).decode("utf8")

    # Return the new plain key to be shown to the user once
    return new_key, key_hash
