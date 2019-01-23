#!/usr/bin/env bash
pytest --cov-report=html --cov=core core/tests/
sensible-browser coverage_html_report/index.html
