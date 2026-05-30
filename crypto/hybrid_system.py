"""
This module handles:
1. Block Cipher Mode (ECB) integration using Member 2's AES implementation.
2. Padding (PKCS#7) handled internally by AES.
3. Hybrid Cryptographic Envelope (bundling RSA + AES + Encodings).
4. Added logs inside the hybrid system to help in debugging and visualizing the hybrid encryption and decryption process.
"""
import os
from . import aes
from . import rsa

# HYBRID WRAPPER (THE CRYPTOGRAPHIC ENVELOPE)

def generate_rsa_keypair(bits=512):
    """Generates an RSA keypair using Member 1's implementation."""
    return rsa.generate_keys(bits)

def generate_aes_key():
    """Generates a random 16-byte (128-bit) session key using the OS CSPRNG."""
    return os.urandom(16)

def hybrid_encrypt(message_string, recipient_pub_key, on_debug=None):
    """
    The full encryption workflow.
    1. Generate AES key.
    2. Encrypt the chat message text with AES (ECB mode).
    3. Encode the AES ciphertext into Hexadecimal text so it's network-safe.
    4. Encrypt the raw AES session key with the recipient's RSA public key.
    5. Return the bundle.

    on_debug(step, data) — optional callback for logging each step.
    """
    _log = on_debug if on_debug else lambda s, d="": None

    # 1. Setup Session Key
    session_key_bytes = generate_aes_key()
    session_key_hex = session_key_bytes.hex()
    _log("[AES] Generated 128-bit Session Key", session_key_hex)

    # 2. Encrypt the message text
    # aes_encrypt takes the string directly and returns ciphertext bytes
    aes_ciphertext_bytes = aes.aes_encrypt(message_string, session_key_hex)
    _log("[AES-ECB] Encrypted Plaintext -> Ciphertext",
         f"{len(aes_ciphertext_bytes)} bytes (PKCS#7 padded)")

    # 3. Encode to safe Base64 strings for network transfer
    import base64
    encoded_ciphertext = base64.b64encode(aes_ciphertext_bytes).decode("utf-8")
    _log("[BASE64] Encoded Ciphertext for Network",
         encoded_ciphertext[:60] + "..." if len(encoded_ciphertext) > 60
         else encoded_ciphertext)

    # 4. RSA Encrypt the Session Key
    # rsa.encrypt takes the bytes directly
    e, n = recipient_pub_key
    _log("[RSA] Encrypting Session Key with Public Key",
         f"e={e}, n={str(n)[:40]}...")
    encrypted_session_key = rsa.encrypt(session_key_bytes, recipient_pub_key)
    _log("[RSA] Encrypted Session Key (Integer)",
         str(encrypted_session_key)[:60] + "..."
         if len(str(encrypted_session_key)) > 60
         else str(encrypted_session_key))

    # 5. Create the transmission bundle
    envelope = {
        "rsa_encrypted_key": encrypted_session_key, # Integer
        "aes_ciphertext_b64": encoded_ciphertext    # String
    }

    _log("[ENVELOPE] Bundle Ready for Transmission",
         f"ciphertext_len={len(encoded_ciphertext)}, "
         f"rsa_key_len={len(str(encrypted_session_key))}")

    return envelope

def hybrid_decrypt(envelope, recipient_priv_key, on_debug=None):
    """
    The full decryption workflow.
    1. Use RSA private key to decrypt the session key.
    2. Decrypt the ciphertext using AES (ECB mode).
    3. Return the original message string.

    on_debug(step, data) — optional callback for logging each step.
    """
    _log = on_debug if on_debug else lambda s, d="": None

    encrypted_session_key = envelope["rsa_encrypted_key"]
    
    # Support both Base64 and legacy Hex ciphertext envelopes
    if "aes_ciphertext_b64" in envelope:
        encoded_ciphertext = envelope["aes_ciphertext_b64"]
    else:
        encoded_ciphertext = envelope.get("aes_ciphertext_hex", "")

    _log("[ENVELOPE] Received Encrypted Bundle",
         f"ciphertext_len={len(encoded_ciphertext)}, "
         f"rsa_key_len={len(str(encrypted_session_key))}")

    # 1. RSA Decrypt the Session Key
    _log("[RSA] Decrypting Session Key with Private Key", "d=***, n=***")
    session_key_bytes = rsa.decrypt(encrypted_session_key, recipient_priv_key)
    session_key_hex = session_key_bytes.hex()
    _log("[RSA] Recovered AES Session Key", session_key_hex)

    # 2 & 3. AES Decrypt
    import base64
    _log("[AES-ECB] Decrypting Ciphertext...",
         encoded_ciphertext[:60] + "..." if len(encoded_ciphertext) > 60
         else encoded_ciphertext)
         
    # Decode string back to raw bytes (Base64)
    ciphertext_bytes = base64.b64decode(encoded_ciphertext)
        
    # Convert ciphertext bytes back to a hex string for our custom scratch AES engine
    ciphertext_hex = ciphertext_bytes.hex()
    
    plaintext_string = aes.aes_decrypt(ciphertext_hex, session_key_hex)
    _log("[AES] Decrypted Plaintext",
         plaintext_string[:60] + "..." if len(plaintext_string) > 60
         else plaintext_string)

    return plaintext_string

