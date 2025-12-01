"""QR code generation utilities for the Mail List Shield application.

This module provides functions for generating QR codes, primarily used
for two-factor authentication setup.
"""

import qrcode
import base64
from io import BytesIO


def qrcode_img_src(qr_string):
    """Generate a base64-encoded QR code image as a data URI.

    Creates a QR code from the given string and returns it as a
    base64-encoded PNG image suitable for use in an HTML img src attribute.

    Args:
        qr_string: The string to encode in the QR code.

    Returns:
        str: A data URI string containing the base64-encoded PNG image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    with BytesIO() as buffer:
        img.save(buffer)
        buffer.seek(0)
        img_bytes = buffer.read()
        base64_string = base64.b64encode(img_bytes).decode("utf-8")
    return "data:image/png;base64," + base64_string
