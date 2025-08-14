#!/usr/bin/env python3
"""
Check Mobile Access - Find running mobile launcher and access info
"""
import json
import os
import sys
from pathlib import Path

def check_mobile_access():
    """Check for mobile access information"""
    claude_dir = Path.home() / '.claude'
    mobile_dir = claude_dir / 'mobile'
    
    print("🔍 Checking Claude Code V3+ Mobile Access Status...")
    print("=" * 60)
    
    # Check if mobile directory exists
    if not mobile_dir.exists():
        print("❌ Mobile directory not found")
        return False
    
    print(f"✅ Mobile directory found: {mobile_dir}")
    
    # Check for current access file
    access_file = mobile_dir / 'current_access.json'
    if access_file.exists():
        try:
            with open(access_file, 'r') as f:
                access_info = json.load(f)
            
            print("\n📱 MOBILE ACCESS FOUND!")
            print("=" * 60)
            print(f"🌐 Mobile URL: {access_info.get('url', 'N/A')}")
            print(f"🔐 Auth Token: {access_info.get('auth_token', 'N/A')}")
            print(f"🚀 Quick Link: {access_info.get('url', 'N/A')}?auth={access_info.get('auth_token', 'N/A')}")
            print(f"⏰ Created: {access_info.get('created', 'N/A')}")
            print(f"⏰ Expires: {access_info.get('expires', 'N/A')}")
            print(f"🔌 Dashboard Port: {access_info.get('dashboard_port', 'N/A')}")
            
            # Check for QR code
            qr_file = access_info.get('qr_file', '')
            if qr_file and Path(qr_file).exists():
                print(f"📱 QR Code: {qr_file}")
            else:
                print("⚠️  QR Code: Not generated")
            
            print("\n📋 To access on Samsung Galaxy S25 Edge:")
            print("1. Copy the Quick Link above")
            print("2. Open Samsung Internet Browser")
            print("3. Paste and navigate to the URL")
            print("4. Full V3+ dashboard access!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading access file: {e}")
            return False
    else:
        print("⚠️  No current access file found")
    
    # Check for auth tokens
    auth_file = mobile_dir / 'auth_tokens.json'
    if auth_file.exists():
        try:
            with open(auth_file, 'r') as f:
                tokens = json.load(f)
            
            print(f"\n🔐 Found {len(tokens)} auth tokens")
            for token, data in tokens.items():
                print(f"Token: {token[:20]}... (expires: {data.get('expires', 'N/A')})")
                
        except Exception as e:
            print(f"❌ Error reading auth tokens: {e}")
    
    # Check for QR code files
    qr_files = list(mobile_dir.glob("*.png"))
    if qr_files:
        print(f"\n📱 Found QR code files:")
        for qr_file in qr_files:
            print(f"  - {qr_file}")
    
    return False

if __name__ == "__main__":
    check_mobile_access()