#!/usr/bin/env python3
"""
📦 Orion Common Imports - Temiz Import Sistemi
🧹 TEMİZ YERDE ÇALIŞMA!
"""

# Standard imports
import logging
import os
import time
import json
from typing import Dict, Any, List
from datetime import datetime

# Utility functions
def get_timestamp():
    return datetime.now().isoformat()

def setup_logger(name):
    return logging.getLogger(name)

print("📦 Common imports ready!")
