"""
Encryption utility for DonutSMP leaderboard data.
Uses AES-256-GCM for authenticated encryption.

The encryption key should be stored as a GitHub secret: ENCRYPTION_KEY_V1
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Current data version - increment when rotating keys
DATA_VERSION = 1

def get_key():
    """Get encryption key from environment variable."""
    key_hex = os.environ.get(f"ENCRYPTION_KEY_V{DATA_VERSION}")
    if not key_hex:
        raise ValueError(f"ENCRYPTION_KEY_V{DATA_VERSION} environment variable not set")
    return bytes.fromhex(key_hex)

def encrypt_file(input_path: str, output_path: str):
    """
    Encrypt a JSON file using AES-256-GCM.
    
    Output format: base64(nonce + ciphertext + tag)
    - nonce: 12 bytes
    - ciphertext: variable
    - tag: 16 bytes (appended by AESGCM)
    """
    key = get_key()
    aesgcm = AESGCM(key)
    
    # Read input file
    with open(input_path, 'r') as f:
        plaintext = f.read().encode('utf-8')
    
    # Generate random nonce (12 bytes for GCM)
    nonce = os.urandom(12)
    
    # Encrypt (AESGCM automatically appends auth tag)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # Encode nonce and ciphertext separately, join with colon
    nonce_b64 = base64.b64encode(nonce).decode('utf-8')
    ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
    encrypted_data = f"{nonce_b64}:{ciphertext_b64}"
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(encrypted_data)
    
    print(f"Encrypted {input_path} -> {output_path}")

def encrypt_all():
    """Encrypt all data files for the current version."""
    version = DATA_VERSION
    
    # Encrypt leaderboards
    if os.path.exists("all_leaderboards.json"):
        encrypt_file("all_leaderboards.json", f"data/leaderboards_v{version}.json.enc")
    
    # Encrypt spawner prices
    if os.path.exists("spawner_prices.json"):
        encrypt_file("spawner_prices.json", f"data/prices_v{version}.json.enc")

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    encrypt_all()
    print(f"Encryption complete for data version {DATA_VERSION}")
