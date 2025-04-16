#! /bin/bash

# Install black for formatting Python code
pip install black

# Install prettier with the Jinja2 plugin for formatting HTML, CSS, and JS
npm install --save-dev prettier prettier-plugin-jinja-template

# Install commitlint for commit message linting
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# Install markdownlint for linting Markdown files
npm install --save-dev markdownlint-cli

# Install pre-commit
pip install pre-commit
pre-commit install --install-hooks

# Install pytest
pip install pytest

# Install pre-commit hooks for the commit-msg stage e.g. for commitlint
pre-commit install --hook-type commit-msg

echo -e "\n--------------------------------\n"
echo -e "You can view the local test database with pgAdmin at \e[1;31mhttp://localhost:5002/\e[0m"
echo -e "The local test database is automatically added as a server in pgAdmin.\n"
echo -e "pgAdmin username: \e[1;31madmin@admin.com\e[0m, password: \e[1;31madmin\e[0m"
echo -e "On first run, when pgAdmin prompts you for the database password, use \e[1;31mpassword\e[0m"
echo -e "\n--------------------------------\n"