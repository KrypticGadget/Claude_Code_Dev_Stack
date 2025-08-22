#!/usr/bin/env python3
"""Weekly maintenance script for repository cleanup."""

import os
import sys
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from maintenance_cleanup import MaintenanceCleanup

def main():
    base_path = Path(__file__).parent.parent
    maintenance = MaintenanceCleanup(str(base_path))
    
    print("Running weekly maintenance...")
    report_path = maintenance.run_maintenance()
    print(f"Weekly maintenance completed. Report: {report_path}")

if __name__ == "__main__":
    main()
