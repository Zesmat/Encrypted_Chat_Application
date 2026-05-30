import os
from . import aes
from . import rsa
import base64

# HYBRID WRAPPER (THE CRYPTOGRAPHIC ENVELOPE)

def generate_rsa_keypair(bits=512):

    return rsa.generate_keys(bits)

def generate_aes_key():

    return os.urandom(16)

def hybrid_encrypt(message_string, recipient_pub_key, on_debug=None):
    
    _log = on_debug if on_debug else lambda s, d="": None

    session_key_bytes = generate_aes_key()
    session_key_hex = session_key_bytes.hex()
    _log("[AES] Generated 128-bit Session Key", session_key_hex)


    aes_ciphertext_bytes = aes.aes_encrypt(message_string, session_key_hex)
    _log("[AES-ECB] Encrypted Plaintext -> Ciphertext",
         f"{len(aes_ciphertext_bytes)} bytes (PKCS#7 padded)")


    encoded_ciphertext = base64.b64encode(aes_ciphertext_bytes).decode("utf-8")
    _log("[BASE64] Encoded Ciphertext for Network",
         encoded_ciphertext[:60] + "..." if len(encoded_ciphertext) > 60
         else encoded_ciphertext)

    e, n = recipient_pub_key
    _log("[RSA] Encrypting Session Key with Public Key",
         f"e={e}, n={str(n)[:40]}...")
    encrypted_session_key = rsa.encrypt(session_key_bytes, recipient_pub_key)
    _log("[RSA] Encrypted Session Key (Integer)",
         str(encrypted_session_key)[:60] + "..."
         if len(str(encrypted_session_key)) > 60
         else str(encrypted_session_key))

    envelope = {
        "rsa_encrypted_key": encrypted_session_key,
        "aes_ciphertext_b64": encoded_ciphertext  
    }

    _log("[ENVELOPE] Bundle Ready for Transmission",
         f"ciphertext_len={len(encoded_ciphertext)}, "
         f"rsa_key_len={len(str(encrypted_session_key))}")

    return envelope

def hybrid_decrypt(envelope, recipient_priv_key, on_debug=None):

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

    _log("[RSA] Decrypting Session Key with Private Key", "d=***, n=***")
    session_key_bytes = rsa.decrypt(encrypted_session_key, recipient_priv_key)
    session_key_hex = session_key_bytes.hex()
    _log("[RSA] Recovered AES Session Key", session_key_hex)

    _log("[AES-ECB] Decrypting Ciphertext...",
         encoded_ciphertext[:60] + "..." if len(encoded_ciphertext) > 60
         else encoded_ciphertext)
         
    ciphertext_bytes = base64.b64decode(encoded_ciphertext)
        
    ciphertext_hex = ciphertext_bytes.hex()
    
    plaintext_string = aes.aes_decrypt(ciphertext_hex, session_key_hex)
    _log("[AES] Decrypted Plaintext",
         plaintext_string[:60] + "..." if len(plaintext_string) > 60
         else plaintext_string)

    return plaintext_string

