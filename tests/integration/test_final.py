#!/usr/bin/env python3
"""
Final test of statusline system - avoid Unicode output issues
"""

import sys
import os

# Add the core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from statusline import (
        StatuslineRenderer, StatuslineConfig, ConfigManager, 
        DefaultTheme
    )
    
    print("[OK] Imports successful")
    
    # Test configuration
    config_manager = ConfigManager()
    config = config_manager._create_default_config()
    print(f"[OK] Config with {len(config.segments)} segments")
    
    # Test renderer
    with StatuslineRenderer(config) as renderer:
        output = renderer.render()
        
        # Write output to file to avoid Unicode issues
        with open('statusline_output.txt', 'w', encoding='utf-8') as f:
            f.write(f"Statusline output: {output}\n")
        
        stats = renderer.get_stats()
        print(f"[OK] Renderer: {stats.render_count} renders, {stats.error_count} errors")
        print(f"[OK] Output written to statusline_output.txt")
    
    print("[SUCCESS] Statusline system is working!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)