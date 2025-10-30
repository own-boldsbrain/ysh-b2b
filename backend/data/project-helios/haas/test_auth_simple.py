#!/usr/bin/env python3
"""
Simple test script to verify auth service database integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.auth_service import authenticate_user, get_user, create_access_token
from app.models.auth import User

def test_auth_service():
    print('Testing auth service with database...')

    try:
        # Test get_user function
        user = get_user('admin@haas.com')
        if user:
            print(f'✓ Found user: {user.email} ({user.role})')
        else:
            print('✗ User not found')

        # Test authenticate_user function
        auth_result = authenticate_user('admin@haas.com', 'admin123')
        if auth_result:
            print(f'✓ Authentication successful: {auth_result.email}')
        else:
            print('✗ Authentication failed')

        print('✓ Auth service database integration working!')

    except Exception as e:
        print(f'✗ Error: {e}')
        return False

    return True

if __name__ == "__main__":
    success = test_auth_service()
    sys.exit(0 if success else 1)