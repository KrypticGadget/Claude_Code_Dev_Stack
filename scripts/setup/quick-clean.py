#!/usr/bin/env python3
"""Quick cleanup script for developers."""

import os
import shutil
from pathlib import Path

def quick_clean():
    base_path = Path.cwd()
    
    # Quick cache cleanup
    cache_patterns = ["__pycache__", "*.pyc", ".mypy_cache", "node_modules/.cache"]
    
    print("Running quick cleanup...")
    
    for pattern in cache_patterns:
        for path in base_path.rglob(pattern):
            if path.is_dir():
                try:
                    shutil.rmtree(path)
                    print(f"Removed: {path}")
                except:
                    pass
            elif path.is_file():
                try:
                    path.unlink()
                    print(f"Removed: {path}")
                except:
                    pass
    
    print("Quick cleanup completed!")

if __name__ == "__main__":
    quick_clean()
