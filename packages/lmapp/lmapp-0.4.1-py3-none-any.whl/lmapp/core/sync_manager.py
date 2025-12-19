import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from loguru import logger
from .auth import GitHubAuth

class SyncManager:
    """
    Manages OPTIONAL encrypted backup of user data to GitHub.
    
    Philosophy:
    - Offline First: This module never blocks the main application.
    - Privacy First: All data is encrypted client-side before leaving the machine.
    - User Control: Only runs if explicitly enabled and authenticated.
    """
    
    def __init__(self, config_dir: Path, auth: GitHubAuth):
        self.config_dir = config_dir
        self.auth = auth
        self.key_file = config_dir / "encryption.key"
        self.cipher_suite: Optional[Fernet] = None
        self._load_or_create_key()

    def _load_or_create_key(self):
        """Load existing encryption key or generate a new one."""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            # Ensure config dir exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            # Save key with restrictive permissions
            with open(self.key_file, "wb") as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)
            
        self.cipher_suite = Fernet(key)

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt string data."""
        if not self.cipher_suite:
            raise RuntimeError("Encryption key not loaded")
        return self.cipher_suite.encrypt(data.encode())

    def decrypt_data(self, token: bytes) -> str:
        """Decrypt bytes to string."""
        if not self.cipher_suite:
            raise RuntimeError("Encryption key not loaded")
        return self.cipher_suite.decrypt(token).decode()

    def sync_up(self, data_path: Path) -> bool:
        """
        Uploads encrypted data to GitHub (Gist or Repo).
        Returns True if successful, False otherwise.
        """
        if not self.auth.is_authenticated():
            logger.warning("Sync skipped: Not authenticated")
            return False

        if not data_path.exists():
            logger.warning(f"Sync skipped: File not found {data_path}")
            return False

        try:
            # 1. Read Data
            with open(data_path, "r") as f:
                raw_data = f.read()

            # 2. Encrypt
            encrypted_data = self.encrypt_data(raw_data)

            # 3. Upload (Placeholder for now - would use Gist API)
            # TODO: Implement actual Gist/Repo upload logic
            logger.info(f"Would upload {len(encrypted_data)} bytes of encrypted data")
            return True

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return False

    def sync_down(self, target_path: Path) -> bool:
        """
        Downloads and decrypts data from GitHub.
        """
        if not self.auth.is_authenticated():
            return False

        try:
            # 1. Download (Placeholder)
            # TODO: Implement actual Gist/Repo download logic
            logger.info("Would download data...")
            
            # encrypted_data = ...
            # decrypted_data = self.decrypt_data(encrypted_data)
            
            # with open(target_path, "w") as f:
            #     f.write(decrypted_data)
            
            return True
        except Exception as e:
            logger.error(f"Sync download failed: {e}")
            return False
