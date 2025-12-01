"""Error handling utilities for the Mail List Shield application.

This module provides functions for rendering error pages.
"""

from flask import render_template
from flask_login import current_user


def error_page(code):
    """Render an error page for the given HTTP status code.

    Args:
        code: The HTTP status code (e.g., 404, 500).

    Returns:
        tuple: A tuple containing (rendered_template, status_code).
    """
    return (render_template(f"public/error_pages/{code}.html", user=current_user), code)
