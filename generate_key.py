#!/usr/bin/env python3
"""
Key Generator for DonutUtility Data Protection

Run this script when you need to rotate to a new data version (scram).
It will generate:
1. A new encryption key for GitHub Actions
2. Obfuscated key parts for the Java mod

Usage:
    python3 generate_key.py [version_number]
    
Example:
    python3 generate_key.py 2
"""

import secrets
import sys

def generate_key_for_version(version: int):
    # Generate a secure 256-bit (32 byte) key
    key_bytes = secrets.token_bytes(32)
    key_hex = key_bytes.hex()
    
    print(f"\n{'='*60}")
    print(f"  KEY GENERATED FOR DATA VERSION {version}")
    print(f"{'='*60}\n")
    
    # GitHub secret
    print("1. ADD THIS TO GITHUB SECRETS:")
    print(f"   Secret name: ENCRYPTION_KEY_V{version}")
    print(f"   Secret value: {key_hex}")
    print()
    
    # XOR mask (can be any 8 bytes, using a simple pattern)
    mask = bytes([0x51, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11])
    
    # Split key into 4 parts and XOR with mask
    parts = []
    for i in range(4):
        part = key_bytes[i*8:(i+1)*8]
        obfuscated = bytes(b ^ mask[j % len(mask)] for j, b in enumerate(part))
        parts.append(obfuscated)
    
    # Generate Java code
    print("2. UPDATE DataManager.java - Replace the key reconstruction block:")
    print()
    print(f"        // Version {version} key parts (obfuscated)")
    print(f"        if (DATA_VERSION == {version}) {{")
    print("            return reconstructKey(")
    print("                // Part 1: bytes 0-7")
    print(f"                new byte[]{{{format_bytes(parts[0])}}},")
    print("                // Part 2: bytes 8-15")
    print(f"                new byte[]{{{format_bytes(parts[1])}}},")
    print("                // Part 3: bytes 16-23")
    print(f"                new byte[]{{{format_bytes(parts[2])}}},")
    print("                // Part 4: bytes 24-31")
    print(f"                new byte[]{{{format_bytes(parts[3])}}},")
    print("                // XOR mask")
    print(f"                new byte[]{{{format_bytes(mask)}}}")
    print("            );")
    print("        }")
    print()
    
    # Update instructions
    print("3. UPDATE encrypt.py:")
    print(f"   Change DATA_VERSION = {version}")
    print()
    
    print("4. UPDATE DataManager.java:")
    print(f"   Change DATA_VERSION = {version}")
    print(f'   Change MOD_VERSION = "1.X.0"  (your new mod version)')
    print()
    
    print("5. UPDATE config.json on GitHub:")
    print(f'   - Mark old version as "revoked" with a message')
    print(f'   - Add new version {version} as "active"')
    print()
    
    print("6. RUN THE GITHUB ACTION to generate new encrypted files")
    print()
    print("7. BUILD AND RELEASE the new mod version on Modrinth")
    print()
    
    # Verification
    print("VERIFICATION - Key reconstruction test:")
    reconstructed = bytearray(32)
    for i in range(4):
        for j in range(8):
            reconstructed[i*8 + j] = parts[i][j] ^ mask[j % len(mask)]
    
    if key_hex == reconstructed.hex():
        print(f"   ✓ Key reconstruction verified successfully!")
    else:
        print(f"   ✗ ERROR: Key reconstruction failed!")
        print(f"   Original:      {key_hex}")
        print(f"   Reconstructed: {reconstructed.hex()}")

def format_bytes(b: bytes) -> str:
    """Format bytes as Java byte array literal."""
    result = []
    for byte in b:
        if byte > 127:
            result.append(f"(byte)0x{byte:02x}")
        else:
            result.append(f"0x{byte:02x}")
    return ", ".join(result)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            version = int(sys.argv[1])
        except ValueError:
            print("Error: Version must be a number")
            sys.exit(1)
    else:
        version = int(input("Enter the new data version number: "))
    
    generate_key_for_version(version)
