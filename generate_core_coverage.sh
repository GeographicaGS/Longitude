#!/usr/bin/env bash
pytest --cov-report=html --cov=src.core src/core/tests/
sensible-browser coverage_html_report/index.html
