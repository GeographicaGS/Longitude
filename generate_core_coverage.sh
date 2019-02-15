#!/usr/bin/env bash
pylint -E longitude --ignore=samples
pytest --cov-report=html --cov=longitude.core longitude/core/tests/
sensible-browser coverage_html_report/index.html
