# =============================================
#  crypto.py — Dummy Cryptography Implementations
# =============================================
#  All functions here are PLACEHOLDERS using simple
#  reversible transforms. Replace each one with the
#  real algorithm when you receive it from your team.
#
#  Member 1: RSA key generation & RSA encrypt/decrypt
#  Member 2: AES encrypt/decrypt
#  Member 3: Hybrid logic (AES key wrapped with RSA)
# =============================================


# ----- RSA (Member 1) -----

def generate_rsa_keypair():
    """
    TODO (Member 1): Replace with real RSA key generation.
    Should return (public_key, private_key) tuple.
    """
    public_key = "(e=65537, n=982451653...)"
    private_key = "(d=123456789, n=982451653...)"
    return public_key, private_key


def rsa_encrypt(plaintext, public_key):
    """
    TODO (Member 1): Replace with real RSA encryption.
    Currently just returns the input unchanged.
    """
    return plaintext


def rsa_decrypt(ciphertext, private_key):
    """
    TODO (Member 1): Replace with real RSA decryption.
    Currently just returns the input unchanged.
    """
    return ciphertext


# ----- AES (Member 2) -----

def generate_aes_key():
    """
    TODO (Member 2): Replace with real AES key generation.
    Should return a proper AES session key.
    """
    return "mock_aes_session_key_128"


def aes_encrypt(plaintext, aes_key):
    """
    TODO (Member 2): Replace with real AES encryption.
    Currently uses hex encoding as a fake cipher.
    """
    return plaintext.encode("utf-8").hex()


def aes_decrypt(ciphertext, aes_key):
    """
    TODO (Member 2): Replace with real AES decryption.
    Currently reverses the hex encoding.
    """
    return bytes.fromhex(ciphertext).decode("utf-8")


# ----- Hybrid / Key Exchange (Member 3) -----

def wrap_aes_key(aes_key, recipient_rsa_public):
    """
    TODO (Member 3): Encrypt the AES session key with the
    recipient's RSA public key so it can be sent over the wire.
    Currently returns the key as-is.
    """
    return aes_key


def unwrap_aes_key(wrapped_key, my_rsa_private):
    """
    TODO (Member 3): Decrypt the wrapped AES key using our
    RSA private key.
    Currently returns the key as-is.
    """
    return wrapped_key
