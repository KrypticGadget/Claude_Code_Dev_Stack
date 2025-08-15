"""
Claude Code Browser Integration - Attribution & License Compliance
================================================================

ORIGINAL WORK:
- Project: Claude Code Browser
- Author: @zainhoda
- License: AGPL-3.0
- Repository: https://github.com/zainhoda/claude-code-browser

INTEGRATION LAYER:
- Created for: Claude Code Dev Stack v3.0
- License: AGPL-3.0 (compatible with original)
- Purpose: Adapter pattern integration maintaining license compliance

This integration extends the original Claude Code Browser functionality
while maintaining full attribution and license compliance requirements.

All modifications and extensions are clearly documented and separated
from the original implementation to respect the AGPL-3.0 license terms.
"""

import os
import json
from typing import Dict, Any

class AttributionManager:
    """Manages attribution and license compliance for integrated components."""
    
    def __init__(self):
        self.attribution_info = {
            "claude_code_browser": {
                "original_author": "@zainhoda",
                "license": "AGPL-3.0",
                "source": "https://github.com/zainhoda/claude-code-browser",
                "description": "Web browser for Claude Code conversation analysis",
                "integration_type": "adapter_pattern",
                "modifications": [
                    "Extended server with Dev Stack API endpoints",
                    "Added WebRTC/noVNC streaming capabilities",
                    "Integrated with PWA monitoring components",
                    "Added real-time WebSocket communication"
                ]
            },
            "dev_stack_extensions": {
                "created_by": "Claude Code Dev Stack v3.0",
                "license": "AGPL-3.0",
                "purpose": "Integration layer for browser monitoring",
                "endpoints_added": [
                    "/api/devstack/agents",
                    "/api/devstack/tasks", 
                    "/api/devstack/hooks",
                    "/api/devstack/audio"
                ]
            }
        }
    
    def get_attribution_notice(self) -> str:
        """Generate attribution notice for display in web interface."""
        return """
        Claude Code Browser Integration
        ==============================
        
        Original Claude Code Browser by @zainhoda
        Licensed under AGPL-3.0
        Source: https://github.com/zainhoda/claude-code-browser
        
        Extended for Claude Code Dev Stack v3.0
        Integration maintains full AGPL-3.0 compliance
        All modifications clearly documented and attributed
        
        This software is free software: you can redistribute it and/or modify
        it under the terms of the GNU Affero General Public License as published
        by the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.
        """
    
    def get_license_info(self) -> Dict[str, Any]:
        """Return comprehensive license information."""
        return {
            "notice": self.get_attribution_notice(),
            "components": self.attribution_info,
            "compliance": {
                "source_available": True,
                "license_file_path": "clones/claude-code-browser/LICENSE",
                "modifications_documented": True,
                "attribution_preserved": True
            }
        }
    
    def generate_attribution_html(self) -> str:
        """Generate HTML attribution notice for web interface."""
        return f"""
        <div class="attribution-notice" style="background: #f5f5f5; padding: 1rem; border-left: 4px solid #0066cc; margin: 1rem 0;">
            <h4>Open Source Attribution</h4>
            <p><strong>Claude Code Browser</strong> by <a href="https://github.com/zainhoda" target="_blank">@zainhoda</a></p>
            <p>Licensed under <a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank">AGPL-3.0</a></p>
            <p>Source: <a href="https://github.com/zainhoda/claude-code-browser" target="_blank">github.com/zainhoda/claude-code-browser</a></p>
            <p><em>Extended with Dev Stack integration while maintaining license compliance</em></p>
        </div>
        """

# Global attribution manager instance
attribution = AttributionManager()