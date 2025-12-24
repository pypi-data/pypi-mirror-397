"""
Core authentication logic - check, login, save
"""
import getpass
import time
from typing import Optional, Tuple
from .api_client import APIClient
from .auth_storage import AuthStorage
from .config import TOKEN_MAX_AGE


class Auth:
    """Main authentication manager"""

    def __init__(self):
        self.api = APIClient()
        self.storage = AuthStorage()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        
        auth_data = self.storage.load()

        if not auth_data or not auth_data.get("token"):
            return False

        # Check if token needs revalidation (> 2 hours old)
        saved_at = auth_data.get("saved_at", 0)
        if time.time() - saved_at > TOKEN_MAX_AGE:
            # Revalidate with server
            user_info = self.api.get_user_info(
                auth_data["token"],
                auth_data.get("tenant_code")
            )

            if not user_info:
                # Token invalid, clear auth
                self.storage.clear()
                return False

            # Token valid, update saved_at timestamp
            self.storage.save(
                username=auth_data["username"],
                token=auth_data["token"],
                tenant_code=auth_data.get("tenant_code"),
                user_info=user_info
            )

        return True

    def login(self, username: Optional[str] = None, password: Optional[str] = None,
              init_models: bool = False) -> bool:
        """
        Interactive login flow

        Args:
            username: Username (will prompt if not provided)
            password: Password (will prompt if not provided)
            init_models: Whether to initialize models after login

        Returns:
            True if login successful, False otherwise
        """
        # Prompt for credentials if not provided
        if not username:
            username = input("Username: ").strip()
        if not password:
            password = getpass.getpass("Password: ")

        # Validate inputs
        if not username or not password:
            print("Username and password required")
            return False

        # Call login API
        print("Authenticating...")
        login_result = self.api.login(username, password)

        if not login_result or not login_result.get("token"):
            print("Login failed: Invalid username or password")
            return False

        token = login_result["token"]
        tenant_code = login_result.get("tenantCode")

        # Get user info
        user_info = self.api.get_user_info(token, tenant_code)

        if not user_info:
            print("Failed to retrieve user info")
            return False

        # Save to storage
        if not self.storage.save(username, token, tenant_code, user_info):
            print("Failed to save credentials")
            return False

        # Extract display name
        display_name = user_info.get('user', {}).get('userName', username)
        print(f"Login successful! Welcome, {display_name}")

        # Optionally initialize models
        if init_models:
            print("\nInitializing models...")
            from .model_manager import ModelManager
            manager = ModelManager()
            manager.initialize_models(token)

        return True

    def logout(self) -> bool:
        """
        Logout user

        Returns:
            True if logout successful
        """
        if self.storage.clear():
            print("Logged out successfully")
            return True
        return False

    def get_user_info(self) -> Optional[dict]:
        """
        Get current user info

        Returns:
            User info dict or None if not authenticated
        """
        auth_data = self.storage.load()
        if auth_data:
            return auth_data.get("user")
        return None

