#!/usr/bin/env python3
"""
BCC Rates - Main module entry point

This allows the package to be run as a module:
    python -m bcc_rates
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
