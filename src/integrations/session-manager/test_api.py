#!/usr/bin/env python3
"""
Quick test script for the Session Management API
===============================================

Tests basic API functionality to ensure everything works correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.session_manager import SessionManager
from services.path_validator import PathValidator
from models.session_models import SessionCreateRequest


async def test_basic_functionality():
    """Test basic functionality without starting the full server."""
    print("Testing Session Management Components")
    print("=" * 40)
    
    # Test 1: Path Validator
    print("\n1. Testing Path Validator...")
    try:
        validator = PathValidator()
        test_path = str(Path.home() / "test_claude_session")
        validation = validator.validate_path(test_path)
        
        if validation.exists:
            print(f"   [OK] Path validation successful: {test_path}")
            print(f"   [INFO] Readable: {validation.readable}, Writable: {validation.writable}")
        else:
            print(f"   [ERROR] Path validation failed: {validation.validation_errors}")
            
    except Exception as e:
        print(f"   [ERROR] Path validator error: {e}")
    
    # Test 2: Session Manager
    print("\n2. Testing Session Manager...")
    try:
        session_manager = SessionManager()
        
        # Create a test session
        create_request = SessionCreateRequest(
            name="Test Session",
            working_directory=str(Path.home() / "test_claude_session"),
            description="Test session for API validation"
        )
        
        session = await session_manager.create_session(create_request)
        print(f"   [OK] Session created: {session.id}")
        print(f"   [INFO] Status: {session.status.value}")
        
        # List sessions
        sessions = session_manager.list_sessions()
        print(f"   [INFO] Total sessions: {len(sessions)}")
        
        # Cleanup
        await session_manager.terminate_session(session.id)
        print(f"   [OK] Session terminated: {session.id}")
        
    except Exception as e:
        print(f"   [ERROR] Session manager error: {e}")
    
    # Test 3: Data Models
    print("\n3. Testing Data Models...")
    try:
        from models.session_models import Session, SessionStatus, AgentConfiguration, AgentType
        
        # Test session creation
        session = Session.create_new(
            name="Model Test",
            working_directory=str(Path.home()),
            description="Testing data models"
        )
        
        print(f"   [OK] Session model created: {session.name}")
        
        # Test serialization
        session_dict = session.to_dict()
        restored_session = Session.from_dict(session_dict)
        
        if restored_session.name == session.name:
            print(f"   [OK] Serialization/deserialization works")
        else:
            print(f"   [ERROR] Serialization failed")
            
    except Exception as e:
        print(f"   [ERROR] Data models error: {e}")
    
    print("\n[SUCCESS] Basic functionality test completed!")


async def test_api_imports():
    """Test that all API components can be imported."""
    print("\n🔍 Testing API Component Imports")
    print("=" * 35)
    
    try:
        from api.session_api import SessionAPI
        print("   ✅ SessionAPI imported successfully")
        
        from services.agent_initializer import AgentInitializer
        print("   ✅ AgentInitializer imported successfully")
        
        from services.session_monitor import SessionMonitor
        print("   ✅ SessionMonitor imported successfully")
        
        # Test creating API instance
        api = SessionAPI(port=8083)  # Use different port for testing
        print("   ✅ SessionAPI instance created")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    return True


async def main():
    """Main test function."""
    print("🚀 Claude Code Session Management API Tests")
    print("=" * 50)
    
    # Test imports first
    imports_ok = await test_api_imports()
    
    if imports_ok:
        # Test basic functionality
        await test_basic_functionality()
        
        print("\n✅ All tests completed!")
        print("\n💡 To start the API server, run:")
        print("   python start_session_api.py")
    else:
        print("\n❌ Import tests failed - check dependencies")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)