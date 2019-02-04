#!/usr/bin/env bash
pytest --cov-report=html --cov=longitude.core longitude/core/tests/
sensible-browser coverage_html_report/index.html
