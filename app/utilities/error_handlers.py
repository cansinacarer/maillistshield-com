from flask import render_template
from flask_login import current_user


def error_page(code):
    return (render_template(f"public/error_pages/{code}.html", user=current_user), code)
