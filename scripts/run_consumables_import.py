#!/usr/bin/env python3
"""Wrapper script to run consumables import using .env credentials"""

import os
import sys
from dotenv import load_dotenv
import subprocess

# Load environment variables from .env
load_dotenv()

# Get credentials
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'f76')

if not db_user or not db_pass:
    print("✗ Error: DB_USER and DB_PASSWORD must be set in .env file")
    sys.exit(1)

# Set environment variables for subprocess
env = os.environ.copy()
env['MYSQL_USER'] = db_user
env['MYSQL_PASS'] = db_pass
env['MYSQL_HOST'] = db_host
env['MYSQL_DB'] = db_name

# Run the consumables import script
result = subprocess.run(
    [sys.executable, '../database/import_consumables_normalized.py'],
    env=env,
    cwd=os.path.dirname(os.path.abspath(__file__))
)

sys.exit(result.returncode)
