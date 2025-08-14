#!/usr/bin/env python3
"""
QR Code Generator - V3.0+ Mobile Access
Generates QR codes for easy mobile access to Claude Code dashboard
"""

import sys
from pathlib import Path
from typing import Optional

def generate_qr_code(data: str, output_file: str = None, display_ascii: bool = True) -> Optional[str]:
    """Generate QR code for mobile access"""
    
    try:
        import qrcode
        from qrcode.console_scripts import main as qr_console
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Save image if output file specified
        saved_file = None
        if output_file:
            try:
                img = qr.make_image(fill_color="black", back_color="white")
                img.save(output_file)
                saved_file = output_file
                print(f"📱 QR code saved: {output_file}")
            except Exception as e:
                print(f"⚠️  Could not save QR code image: {e}")
        
        # Display ASCII QR code
        if display_ascii:
            print("\n📱 QR Code for Mobile Access:")
            print("=" * 50)
            try:
                qr.print_ascii(invert=True)
            except:
                # Fallback ASCII display
                qr_ascii = qrcode.QRCode()
                qr_ascii.add_data(data)
                qr_ascii.make()
                qr_ascii.print_ascii()
            print("=" * 50)
            print(f"📱 Scan with camera app or QR reader")
            print(f"🔗 Or manually enter: {data}")
        
        return saved_file
        
    except ImportError:
        print("⚠️  QR code generation requires 'qrcode' package")
        print("📦 Install with: pip install qrcode[pil]")
        print(f"🔗 Manual URL: {data}")
        return None
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        print(f"🔗 Manual URL: {data}")
        return None

def generate_mobile_access_qr(url: str, auth_token: str, output_dir: str = None) -> Optional[str]:
    """Generate QR code specifically for mobile dashboard access"""
    
    # Create complete access URL
    access_url = f"{url}?auth={auth_token}"
    
    # Determine output file
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_file = str(output_dir / 'mobile_access_qr.png')
    else:
        output_file = 'mobile_access_qr.png'
    
    print("🔐 Generating secure mobile access QR code...")
    print(f"🌐 URL: {url}")
    print(f"🔑 Token: {auth_token[:16]}...{auth_token[-8:]}")
    
    # Generate QR code
    saved_file = generate_qr_code(access_url, output_file, display_ascii=True)
    
    if saved_file:
        print(f"✅ QR code ready for Samsung Galaxy S25 Edge!")
        print(f"📁 File: {saved_file}")
    
    return saved_file

def create_fallback_ascii_qr(data: str) -> str:
    """Create simple ASCII QR code fallback"""
    try:
        # Very basic ASCII QR code representation
        lines = []
        lines.append("┌" + "─" * 30 + "┐")
        lines.append("│ QR CODE FOR MOBILE ACCESS   │")
        lines.append("├" + "─" * 30 + "┤")
        
        # Split URL into chunks for display
        chunk_size = 28
        url_chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        for chunk in url_chunks:
            lines.append(f"│ {chunk:<28} │")
        
        lines.append("└" + "─" * 30 + "┘")
        
        return "\n".join(lines)
        
    except:
        return f"Manual URL: {data}"

def main():
    """CLI for QR code generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate QR codes for Claude Code mobile access')
    parser.add_argument('data', help='Data to encode in QR code')
    parser.add_argument('--output', '-o', help='Output image file')
    parser.add_argument('--no-ascii', action='store_true', help='Don\'t display ASCII QR code')
    parser.add_argument('--mobile-access', action='store_true', help='Format as mobile access URL')
    parser.add_argument('--auth-token', help='Authentication token for mobile access')
    
    args = parser.parse_args()
    
    if args.mobile_access and args.auth_token:
        # Generate mobile access QR
        output_dir = Path(args.output).parent if args.output else None
        generate_mobile_access_qr(args.data, args.auth_token, output_dir)
    else:
        # Generate regular QR code
        generate_qr_code(args.data, args.output, not args.no_ascii)

if __name__ == '__main__':
    main()