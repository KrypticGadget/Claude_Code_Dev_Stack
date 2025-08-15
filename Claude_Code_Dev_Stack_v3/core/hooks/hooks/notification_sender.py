#!/usr/bin/env python3
"""
Notification Sender Hook - V3.0+ Remote Monitoring
Sends notifications to Android/iOS devices via Pushover, Telegram, or webhooks
Parallel to audio_player_v3.py but for remote notifications
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading
import time

class NotificationSender:
    """Remote notification system for Claude Code operations"""
    
    def __init__(self):
        # Load settings
        self.settings = self.load_settings()
        self.enabled = self.settings.get('v3ExtendedFeatures', {}).get('notifications', {}).get('enabled', True)
        
        # Notification services
        self.pushover_token = os.getenv('PUSHOVER_TOKEN')
        self.pushover_user = os.getenv('PUSHOVER_USER')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.webhook_url = os.getenv('NOTIFICATION_WEBHOOK')
        
        # Priority settings
        self.priorities = self.settings.get('v3ExtendedFeatures', {}).get('notifications', {}).get('priorities', {})
        
        # Quiet hours
        quiet_config = self.settings.get('v3ExtendedFeatures', {}).get('notifications', {}).get('quietHours', {})
        self.quiet_hours_enabled = quiet_config.get('enabled', False)
        self.quiet_start = quiet_config.get('start', '22:00')
        self.quiet_end = quiet_config.get('end', '08:00')
        
        # Notification mapping (audio event -> notification)
        self.audio_to_notification = {
            # Critical Events (Always Send)
            'command_failed.wav': ('Command Failed', 'Command execution failed', 2),
            'tests_failed.wav': ('Tests Failed', 'Test suite failed', 2),
            'token_critical.wav': ('Token Critical', 'Token usage at 90% - handoff recommended', 2),
            'handoff_generated.wav': ('Handoff Ready', 'Handoff documentation generated', 2),
            'connection_error.wav': ('Connection Error', 'Network connection failed', 2),
            'permission_denied.wav': ('Permission Denied', 'Access denied to resource', 2),
            
            # High Priority
            'performance_warning.wav': ('Performance Warning', 'Performance threshold exceeded', 1),
            'resource_warning.wav': ('Resource Warning', 'High resource usage detected', 1),
            'venv_required.wav': ('Venv Required', 'Virtual environment required but not active', 1),
            'linting_issues.wav': ('Linting Issues', 'Code quality issues detected', 1),
            
            # Phase Transitions (Normal)
            'phase_planning.wav': ('Planning Phase', 'Entered planning phase', 0),
            'phase_implementation.wav': ('Implementation', 'Started implementation phase', 0),
            'phase_testing.wav': ('Testing Phase', 'Running test suite', 0),
            'phase_deployment.wav': ('Deployment', 'Deploying to production', 0),
            'phase_complete.wav': ('Phase Complete', 'Phase completed successfully', 0),
            
            # Operations (Normal)
            'project_created.wav': ('Project Created', 'New project initialized', 0),
            'build_successful.wav': ('Build Success', 'Build completed successfully', 0),
            'tests_passed.wav': ('Tests Passed', 'All tests passed', 0),
            'orchestration_started.wav': ('Orchestration', 'Multi-agent orchestration started', 0),
            'orchestration_complete.wav': ('Complete', 'Orchestration completed', 0),
            
            # Git Operations (Low)
            'git_commit.wav': ('Git Commit', 'Changes committed', -1),
            'git_push.wav': ('Git Push', 'Pushed to remote', -1),
            'git_pull.wav': ('Git Pull', 'Pulled latest changes', -1),
            
            # New V3+ Events
            'tunnel_connected.wav': ('Tunnel Connected', 'Remote access established', 0),
            'tunnel_disconnected.wav': ('Tunnel Lost', 'Remote access disconnected', 1),
            'dashboard_started.wav': ('Dashboard Active', 'Monitoring dashboard started', 0),
            'notification_sent.wav': ('Notification Sent', 'Remote notification delivered', -2),
            'quality_gate_passed.wav': ('Quality Pass', 'All quality checks passed', -1)
        }
        
        # State tracking
        self.last_notification = {}
        self.notification_cooldown = 60  # seconds between same notification
        
        # Start notification thread
        self.notification_queue = []
        self.notification_thread = threading.Thread(target=self.notification_worker, daemon=True)
        self.notification_thread.start()
    
    def load_settings(self) -> Dict:
        """Load settings from settings.json"""
        settings_path = Path.home() / '.claude' / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def is_quiet_hours(self) -> bool:
        """Check if current time is in quiet hours"""
        if not self.quiet_hours_enabled:
            return False
        
        now = datetime.now().time()
        start = datetime.strptime(self.quiet_start, '%H:%M').time()
        end = datetime.strptime(self.quiet_end, '%H:%M').time()
        
        if start <= end:
            return start <= now <= end
        else:  # Crosses midnight
            return now >= start or now <= end
    
    def should_send(self, event: str, priority: int) -> bool:
        """Determine if notification should be sent"""
        if not self.enabled:
            return False
        
        # Always send critical (priority 2)
        if priority >= 2:
            return True
        
        # Check quiet hours for non-critical
        if self.is_quiet_hours():
            return False
        
        # Check cooldown
        if event in self.last_notification:
            elapsed = time.time() - self.last_notification[event]
            if elapsed < self.notification_cooldown:
                return False
        
        return True
    
    def queue_notification(self, title: str, message: str, priority: int = 0, data: Dict = None):
        """Queue notification for sending"""
        notification = {
            'title': title,
            'message': message,
            'priority': priority,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }
        self.notification_queue.append(notification)
    
    def notification_worker(self):
        """Background worker to send notifications"""
        while True:
            if self.notification_queue:
                notification = self.notification_queue.pop(0)
                self.send_notification(
                    notification['title'],
                    notification['message'],
                    notification['priority'],
                    notification['data']
                )
            time.sleep(0.5)
    
    def send_notification(self, title: str, message: str, priority: int = 0, data: Dict = None):
        """Send notification to all configured channels"""
        # Prepend with Claude Code identifier
        title = f"Claude Code: {title}"
        
        # Add context to message
        if data:
            if 'agent' in data:
                message = f"[{data['agent']}] {message}"
            if 'file' in data:
                message = f"{message}\nFile: {data['file']}"
        
        # Send to each service
        success = False
        
        if self.pushover_token and self.pushover_user:
            success = self.send_pushover(title, message, priority) or success
        
        if self.telegram_bot_token and self.telegram_chat_id:
            success = self.send_telegram(title, message, priority) or success
        
        if self.webhook_url:
            success = self.send_webhook(title, message, priority, data) or success
        
        return success
    
    def send_pushover(self, title: str, message: str, priority: int) -> bool:
        """Send notification via Pushover"""
        try:
            # Map priority: -2 to 2 -> -2 to 2 (Pushover scale)
            pushover_priority = max(-2, min(2, priority))
            
            # Select sound based on priority
            sounds = {
                2: 'siren',      # Critical
                1: 'persistent', # High
                0: 'pushover',   # Normal
                -1: 'none',      # Low
                -2: 'none'       # Lowest
            }
            
            data = {
                'token': self.pushover_token,
                'user': self.pushover_user,
                'title': title,
                'message': message,
                'priority': pushover_priority,
                'sound': sounds.get(priority, 'pushover'),
                'timestamp': int(time.time())
            }
            
            # Require acknowledgment for critical
            if priority >= 2:
                data['retry'] = 60  # Retry every 60 seconds
                data['expire'] = 3600  # Expire after 1 hour
            
            response = requests.post(
                'https://api.pushover.net/1/messages.json',
                data=data,
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Pushover error: {e}")
            return False
    
    def send_telegram(self, title: str, message: str, priority: int) -> bool:
        """Send notification via Telegram"""
        try:
            # Format message with emoji based on priority
            emojis = {
                2: '🚨',   # Critical
                1: '⚠️',   # High
                0: '📢',   # Normal
                -1: '💬',  # Low
                -2: '🔇'   # Lowest
            }
            
            emoji = emojis.get(priority, '📢')
            formatted_message = f"{emoji} *{title}*\n\n{message}"
            
            # For critical, add buttons
            keyboard = None
            if priority >= 2:
                keyboard = {
                    'inline_keyboard': [[
                        {'text': 'View Dashboard', 'url': f'http://localhost:8080'},
                        {'text': 'Acknowledge', 'callback_data': 'ack'}
                    ]]
                }
            
            data = {
                'chat_id': self.telegram_chat_id,
                'text': formatted_message,
                'parse_mode': 'Markdown',
                'disable_notification': priority < 0  # Silent for low priority
            }
            
            if keyboard:
                data['reply_markup'] = json.dumps(keyboard)
            
            response = requests.post(
                f'https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage',
                json=data,
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Telegram error: {e}")
            return False
    
    def send_webhook(self, title: str, message: str, priority: int, data: Dict = None) -> bool:
        """Send notification via webhook"""
        try:
            payload = {
                'title': title,
                'message': message,
                'priority': priority,
                'timestamp': datetime.now().isoformat(),
                'source': 'claude-code-v3',
                'data': data or {}
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            
            return response.status_code in [200, 201, 204]
            
        except Exception as e:
            print(f"Webhook error: {e}")
            return False
    
    def handle_audio_event(self, audio_file: str, context: Dict = None):
        """Handle audio event and send notification if mapped"""
        if audio_file in self.audio_to_notification:
            title, message, priority = self.audio_to_notification[audio_file]
            
            if self.should_send(audio_file, priority):
                self.queue_notification(title, message, priority, context)
                self.last_notification[audio_file] = time.time()
    
    def send_custom(self, title: str, message: str, priority: int = 0):
        """Send custom notification"""
        if self.enabled:
            self.queue_notification(title, message, priority)

# Global instance
_notification_sender = None

def get_sender():
    """Get or create notification sender instance"""
    global _notification_sender
    if _notification_sender is None:
        _notification_sender = NotificationSender()
    return _notification_sender

def main():
    """Hook entry point"""
    import sys
    
    sender = get_sender()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == 'audio-event' and len(sys.argv) > 2:
            # Handle audio event
            audio_file = sys.argv[2]
            context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            sender.handle_audio_event(audio_file, context)
        
        elif action == 'custom' and len(sys.argv) > 3:
            # Send custom notification
            title = sys.argv[2]
            message = sys.argv[3]
            priority = int(sys.argv[4]) if len(sys.argv) > 4 else 0
            sender.send_custom(title, message, priority)
        
        elif action == 'test':
            # Test notification
            sender.send_custom(
                "Test Notification",
                "Claude Code V3.0+ notification system is working!",
                1
            )
            print("Test notification sent!")

if __name__ == '__main__':
    main()