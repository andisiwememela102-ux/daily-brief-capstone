"""Sphinx configuration for the Django news application."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_project.settings")

import django

django.setup()

project = "The Daily Brief"
author = "Andisiwe Memela"
release = "1.0.0"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]
templates_path = ["_templates"]
exclude_patterns = ["_build"]
html_theme = "alabaster"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
