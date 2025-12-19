"""
upif.core.licensing
~~~~~~~~~~~~~~~~~~~

Manages Commercial Licensing and Feature Unlocking.
Integrates with Gumroad API for key verification and uses local AES encryption
to cache license state offline.

:copyright: (c) 2025 Yash Dhone.
:license: Proprietary, see LICENSE for details.
"""

import os
import json
import logging
import requests
import base64
from typing import Optional, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger("upif.licensing")

class LicenseManager:
    """
    License Manager.
    
    Security Note: 
    In a real-world scenario, the '_INTERNAL_KEY' and salt should be:
    1. Obfuscated via Cython compilation (which we do in build.py).
    2. Ideally fetched from a separate secure enclave or injected at build time.
    """
    
    # Placeholder: Developer should replace this
    PRODUCT_PERMALINK = "xokvjp" 
    
    # Obfuscated internal key material (Static for Demo)
    _INTERNAL_SALT = b'upif_secure_salt_2025'
    _INTERNAL_KEY = b'static_key_for_demo_purposes_only'

    def __init__(self, storage_path: str = ".upif_license.enc"):
        self.storage_path = storage_path
        self._cipher = self._get_cipher()
        self.license_data: Optional[Dict] = None

    def _get_cipher(self) -> Fernet:
        """Derives a strong AES-256 key from the internal secret using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._INTERNAL_SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self._INTERNAL_KEY))
        return Fernet(key)

    def activate(self, license_key: str, product_permalink: Optional[str] = None) -> bool:
        """
        Activates the license online via Gumroad API.
        
        Args:
            license_key (str): The user's key (e.g. from email).
            product_permalink (str, optional): Override product ID.

        Returns:
            bool: True if activation successful.
        """
        permalink = product_permalink or self.PRODUCT_PERMALINK
        url = "https://api.gumroad.com/v2/licenses/verify"
        
        try:
            logger.info(f"Contacting License Server...")
            # Timeout is critical to avoid hanging app startup
            response = requests.post(url, data={
                "product_permalink": permalink,
                "license_key": license_key
            }, timeout=10)
            
            data = response.json()
            
            if data.get("success") is True:
                # Valid License: Cache minimal data locally
                self.license_data = {
                    "key": license_key,
                    "uses": data.get("uses"),
                    "email": data.get("purchase", {}).get("email"),
                    "timestamp": data.get("purchase", {}).get("created_at"),
                    "tier": "PRO" # Logic to distinguish tiers could go here
                }
                self._save_local()
                logger.info("License Activated. PRO Features Unlocked.")
                return True
            else:
                logger.error(f"License Activation Failed: {data.get('message')}")
                return False
                
        except Exception as e:
            logger.error(f"License Verification Network Error: {e}")
            return False

    def validate_offline(self) -> bool:
        """
        Checks for a valid, tamper-evident local license file.
        Useful for air-gapped or offline startups.
        """
        if self.license_data:
            return True
        return self._load_local()

    def _save_local(self) -> None:
        """Encrypts and persists the license state."""
        if not self.license_data:
            return
            
        try:
            raw_json = json.dumps(self.license_data).encode('utf-8')
            encrypted = self._cipher.encrypt(raw_json)
            with open(self.storage_path, "wb") as f:
                f.write(encrypted)
        except Exception as e:
            logger.error(f"Failed to persist license: {e}")

    def _load_local(self) -> bool:
        """Decrypts and validates the local license file."""
        if not os.path.exists(self.storage_path):
            return False
            
        try:
            with open(self.storage_path, "rb") as f:
                encrypted = f.read()
                
            decrypted = self._cipher.decrypt(encrypted)
            self.license_data = json.loads(decrypted.decode('utf-8'))
            return True
        except Exception:
            # Decryption failure implies file tampering or wrong key
            logger.warning("Local license file corrupted or tampered.")
            return False

    def get_tier(self) -> str:
        """Returns 'PRO' or 'BASELINE'."""
        if self.validate_offline():
            return self.license_data.get("tier", "BASELINE")
        return "BASELINE"
