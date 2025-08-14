#!/usr/bin/env python3
"""
Mobile Authentication System - V3.0+ Security
Handles secure token-based authentication for mobile dashboard access
"""

import os
import json
import time
import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from functools import wraps

class MobileAuthManager:
    """Manages secure authentication for mobile dashboard access"""
    
    def __init__(self, auth_dir: Path = None):
        self.auth_dir = auth_dir or (Path.home() / '.claude' / 'mobile')
        self.auth_dir.mkdir(parents=True, exist_ok=True)
        
        # Token storage
        self.tokens_file = self.auth_dir / 'auth_tokens.json'
        self.sessions_file = self.auth_dir / 'active_sessions.json'
        
        # Security settings
        self.token_expiry = 24 * 60 * 60  # 24 hours
        self.max_sessions = 5  # Max concurrent sessions
        self.rate_limit_window = 60  # 1 minute
        self.max_attempts = 10  # Max attempts per window
        
        # Rate limiting storage
        self.rate_limits = {}  # IP -> [timestamps]
        
        # Load existing data
        self.tokens = self.load_tokens()
        self.sessions = self.load_sessions()
    
    def load_tokens(self) -> Dict:
        """Load stored authentication tokens"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    tokens = json.load(f)
                # Clean expired tokens
                current_time = int(time.time())
                return {k: v for k, v in tokens.items() if v.get('expires', 0) > current_time}
            except:
                pass
        return {}
    
    def save_tokens(self):
        """Save authentication tokens to file"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save auth tokens: {e}")
    
    def load_sessions(self) -> Dict:
        """Load active sessions"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    sessions = json.load(f)
                # Clean expired sessions
                current_time = int(time.time())
                return {k: v for k, v in sessions.items() if v.get('expires', 0) > current_time}
            except:
                pass
        return {}
    
    def save_sessions(self):
        """Save active sessions to file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save sessions: {e}")
    
    def generate_token(self, metadata: Dict = None) -> Tuple[str, Dict]:
        """Generate new authentication token"""
        # Create secure token
        token = secrets.token_urlsafe(32)
        
        # Create token data
        current_time = int(time.time())
        token_data = {
            'token': token,
            'created': current_time,
            'expires': current_time + self.token_expiry,
            'metadata': metadata or {},
            'used': False,
            'usage_count': 0,
            'last_used': None
        }
        
        # Store token
        self.tokens[token] = token_data
        self.save_tokens()
        
        return token, token_data
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate authentication token"""
        if not token or token not in self.tokens:
            return False, None
        
        token_data = self.tokens[token]
        current_time = int(time.time())
        
        # Check expiry
        if token_data.get('expires', 0) <= current_time:
            # Clean up expired token
            del self.tokens[token]
            self.save_tokens()
            return False, None
        
        # Update usage
        token_data['used'] = True
        token_data['usage_count'] = token_data.get('usage_count', 0) + 1
        token_data['last_used'] = current_time
        self.save_tokens()
        
        return True, token_data
    
    def create_session(self, token: str, ip_address: str, user_agent: str = "") -> Optional[str]:
        """Create authenticated session"""
        # Validate token first
        valid, token_data = self.validate_token(token)
        if not valid:
            return None
        
        # Check session limits
        active_count = len([s for s in self.sessions.values() 
                           if s.get('expires', 0) > time.time()])
        
        if active_count >= self.max_sessions:
            # Remove oldest session
            oldest_session = min(self.sessions.items(), 
                               key=lambda x: x[1].get('created', 0))
            del self.sessions[oldest_session[0]]
        
        # Generate session ID
        session_id = secrets.token_urlsafe(24)
        
        # Create session data
        current_time = int(time.time())
        session_data = {
            'session_id': session_id,
            'token': token,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created': current_time,
            'expires': current_time + self.token_expiry,
            'last_activity': current_time,
            'requests': 0
        }
        
        # Store session
        self.sessions[session_id] = session_data
        self.save_sessions()
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str = None) -> Tuple[bool, Optional[Dict]]:
        """Validate active session"""
        if not session_id or session_id not in self.sessions:
            return False, None
        
        session_data = self.sessions[session_id]
        current_time = int(time.time())
        
        # Check expiry
        if session_data.get('expires', 0) <= current_time:
            del self.sessions[session_id]
            self.save_sessions()
            return False, None
        
        # Check IP address if provided
        if ip_address and session_data.get('ip_address') != ip_address:
            # IP mismatch - possible session hijacking
            return False, None
        
        # Update activity
        session_data['last_activity'] = current_time
        session_data['requests'] = session_data.get('requests', 0) + 1
        self.save_sessions()
        
        return True, session_data
    
    def revoke_token(self, token: str) -> bool:
        """Revoke authentication token"""
        if token in self.tokens:
            del self.tokens[token]
            self.save_tokens()
            
            # Also remove associated sessions
            sessions_to_remove = [sid for sid, data in self.sessions.items() 
                                 if data.get('token') == token]
            for sid in sessions_to_remove:
                del self.sessions[sid]
            self.save_sessions()
            
            return True
        return False
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke active session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.save_sessions()
            return True
        return False
    
    def check_rate_limit(self, ip_address: str) -> bool:
        """Check if IP is rate limited"""
        current_time = time.time()
        
        # Clean old entries
        if ip_address in self.rate_limits:
            self.rate_limits[ip_address] = [
                t for t in self.rate_limits[ip_address] 
                if current_time - t < self.rate_limit_window
            ]
        else:
            self.rate_limits[ip_address] = []
        
        # Check limit
        if len(self.rate_limits[ip_address]) >= self.max_attempts:
            return False
        
        # Add current attempt
        self.rate_limits[ip_address].append(current_time)
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        if session_id in self.sessions:
            session_data = self.sessions[session_id].copy()
            # Don't expose sensitive token
            session_data.pop('token', None)
            return session_data
        return None
    
    def list_active_sessions(self) -> List[Dict]:
        """List all active sessions"""
        current_time = int(time.time())
        active_sessions = []
        
        for session_id, data in self.sessions.items():
            if data.get('expires', 0) > current_time:
                session_info = data.copy()
                session_info.pop('token', None)  # Don't expose token
                session_info['session_id'] = session_id
                active_sessions.append(session_info)
        
        return sorted(active_sessions, key=lambda x: x.get('created', 0), reverse=True)
    
    def cleanup_expired(self):
        """Clean up expired tokens and sessions"""
        current_time = int(time.time())
        
        # Clean tokens
        expired_tokens = [k for k, v in self.tokens.items() 
                         if v.get('expires', 0) <= current_time]
        for token in expired_tokens:
            del self.tokens[token]
        
        # Clean sessions
        expired_sessions = [k for k, v in self.sessions.items() 
                           if v.get('expires', 0) <= current_time]
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_tokens or expired_sessions:
            self.save_tokens()
            self.save_sessions()
        
        return len(expired_tokens), len(expired_sessions)
    
    def get_stats(self) -> Dict:
        """Get authentication statistics"""
        current_time = int(time.time())
        
        active_tokens = len([t for t in self.tokens.values() 
                           if t.get('expires', 0) > current_time])
        active_sessions = len([s for s in self.sessions.values() 
                             if s.get('expires', 0) > current_time])
        
        return {
            'active_tokens': active_tokens,
            'active_sessions': active_sessions,
            'total_tokens_created': len(self.tokens),
            'rate_limited_ips': len([ip for ip, attempts in self.rate_limits.items() 
                                   if len(attempts) >= self.max_attempts]),
            'current_time': current_time
        }

# Flask authentication decorators
def create_auth_decorators(auth_manager: MobileAuthManager):
    """Create Flask authentication decorators"""
    
    def require_auth(f):
        """Decorator to require authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify, session as flask_session
            
            # Get IP address
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR') or request.remote_addr
            
            # Check rate limiting
            if not auth_manager.check_rate_limit(ip_address):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Check for token in various places
            auth_token = None
            session_id = None
            
            # 1. URL parameter
            auth_token = request.args.get('auth')
            
            # 2. Authorization header
            if not auth_token:
                auth_header = request.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    auth_token = auth_header[7:]
            
            # 3. Session cookie
            if not auth_token:
                session_id = flask_session.get('claude_session_id')
            
            # Validate authentication
            if session_id:
                # Validate existing session
                valid, session_data = auth_manager.validate_session(session_id, ip_address)
                if not valid:
                    flask_session.pop('claude_session_id', None)
                    return jsonify({'error': 'Invalid session'}), 401
            elif auth_token:
                # Create new session from token
                valid, token_data = auth_manager.validate_token(auth_token)
                if not valid:
                    return jsonify({'error': 'Invalid token'}), 401
                
                # Create session
                user_agent = request.headers.get('User-Agent', '')
                session_id = auth_manager.create_session(auth_token, ip_address, user_agent)
                if session_id:
                    flask_session['claude_session_id'] = session_id
                else:
                    return jsonify({'error': 'Could not create session'}), 500
            else:
                return jsonify({'error': 'Authentication required'}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def require_session(f):
        """Decorator to require valid session (lighter than full auth)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify, session as flask_session
            
            # Get session ID
            session_id = flask_session.get('claude_session_id')
            if not session_id:
                return jsonify({'error': 'Session required'}), 401
            
            # Validate session
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR') or request.remote_addr
            valid, session_data = auth_manager.validate_session(session_id, ip_address)
            
            if not valid:
                flask_session.pop('claude_session_id', None)
                return jsonify({'error': 'Invalid session'}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return require_auth, require_session

def main():
    """CLI for mobile auth management"""
    import sys
    
    auth_manager = MobileAuthManager()
    
    if len(sys.argv) < 2:
        print("Usage: mobile_auth.py <action>")
        print("Actions:")
        print("  generate         - Generate new auth token")
        print("  validate <token> - Validate token")
        print("  revoke <token>   - Revoke token")
        print("  sessions         - List active sessions")
        print("  cleanup          - Clean expired tokens/sessions")
        print("  stats            - Show authentication stats")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'generate':
        token, data = auth_manager.generate_token()
        print(f"Generated token: {token}")
        print(f"Expires: {datetime.fromtimestamp(data['expires']).isoformat()}")
    
    elif action == 'validate' and len(sys.argv) > 2:
        token = sys.argv[2]
        valid, data = auth_manager.validate_token(token)
        if valid:
            print(f"Token valid - expires: {datetime.fromtimestamp(data['expires']).isoformat()}")
        else:
            print("Token invalid or expired")
    
    elif action == 'revoke' and len(sys.argv) > 2:
        token = sys.argv[2]
        if auth_manager.revoke_token(token):
            print("Token revoked")
        else:
            print("Token not found")
    
    elif action == 'sessions':
        sessions = auth_manager.list_active_sessions()
        print(f"Active sessions: {len(sessions)}")
        for session in sessions:
            created = datetime.fromtimestamp(session['created']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {session['session_id'][:16]}... - {session['ip_address']} - {created}")
    
    elif action == 'cleanup':
        expired_tokens, expired_sessions = auth_manager.cleanup_expired()
        print(f"Cleaned up {expired_tokens} tokens and {expired_sessions} sessions")
    
    elif action == 'stats':
        stats = auth_manager.get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()