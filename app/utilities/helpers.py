from random import randrange
import uuid

from app import bc


# Returns the file/folder size given in bytes in the appropriate units as text
def readable_file_size(size_in_bytes, significant_digits=0):
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
    code = ""
    for i in range(n):
        code = code + str(randrange(9) + 1)
    return code


def generate_api_key_and_hash():
    # Generate a new random key
    new_key = uuid.uuid4().hex + uuid.uuid4().hex  # 64 characters

    # Hash the key to be stored in the database
    key_hash = bc.generate_password_hash(new_key).decode("utf8")

    # Return the new plain key to be shown to the user once
    return new_key, key_hash
