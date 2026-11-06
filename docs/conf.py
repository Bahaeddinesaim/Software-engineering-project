"""Sphinx configuration for the French technical documentation."""

project = "TelcoGuard AI"
author = "SAIM Bahaeddine"
copyright = "2026, SAIM Bahaeddine"
release = "1.0.0"
language = "fr"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode"]
html_theme = "alabaster"
exclude_patterns = ["_build"]
