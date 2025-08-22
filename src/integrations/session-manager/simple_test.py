#!/usr/bin/env python3
"""
Simple test for Session Management API (ASCII only)
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    """Simple test of core components."""
    print("Claude Code Session Management API - Simple Test")
    print("=" * 50)
    
    try:
        # Test 1: Import models
        print("\n1. Testing imports...")
        from models.session_models import Session, SessionCreateRequest
        print("   [OK] Models imported")
        
        # Test 2: Path validator
        from services.path_validator import PathValidator
        validator = PathValidator()
        test_path = str(Path.home() / "test_claude")
        validation = validator.validate_path(test_path)
        print(f"   [OK] Path validator works: {validation.exists}")
        
        # Test 3: Session manager
        from core.session_manager import SessionManager
        session_manager = SessionManager()
        print("   [OK] Session manager created")
        
        # Test 4: Create session
        request = SessionCreateRequest(
            name="Test Session",
            working_directory=test_path,
            description="Simple test"
        )
        session = await session_manager.create_session(request)
        print(f"   [OK] Session created: {session.id}")
        
        # Test 5: List sessions
        sessions = session_manager.list_sessions()
        print(f"   [OK] Found {len(sessions)} sessions")
        
        # Test 6: Terminate session
        await session_manager.terminate_session(session.id)
        print("   [OK] Session terminated")
        
        print("\n[SUCCESS] All basic tests passed!")
        print("\nTo start the full API server:")
        print("  python start_session_api.py")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)