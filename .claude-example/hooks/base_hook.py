#!/usr/bin/env python3
"""Base hook utilities for Claude Code Dev Stack"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_claude_home():
    """Get Claude home directory"""
    return Path(os.environ.get('CLAUDE_HOME', Path.home() / '.claude')).expanduser()

def get_project_dir():
    """Get current project directory"""
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())).resolve()

def load_config(config_name='settings.json'):
    """Load configuration file"""
    config_paths = [
        get_project_dir() / '.claude' / config_name,
        get_claude_home() / config_name
    ]
    
    for path in config_paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config from {path}: {e}")
    
    return {}

def save_state(state_data, filename):
    """Save state to file"""
    state_dir = get_claude_home() / 'state'
    state_dir.mkdir(parents=True, exist_ok=True)
    
    state_file = state_dir / filename
    try:
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save state to {state_file}: {e}")
        return False

def load_state(filename):
    """Load state from file"""
    state_file = get_claude_home() / 'state' / filename
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state from {state_file}: {e}")
    return {}

def log_event(event_type, data):
    """Log an event"""
    log_dir = get_claude_home() / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"hooks_{datetime.now().strftime('%Y%m%d')}.log"
    
    event = {
        'timestamp': datetime.now().isoformat(),
        'type': event_type,
        'data': data
    }
    
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    except Exception as e:
        logger.error(f"Failed to log event: {e}")

def exit_gracefully(code=0):
    """Exit without blocking Claude Code"""
    sys.exit(code)