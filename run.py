"""Entry point for running the Mail List Shield Flask application.

This module creates and runs the Flask application using the application
factory pattern defined in the app package.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
