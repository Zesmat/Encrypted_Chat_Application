"""
Encoding Module - Member 3

ENCODING EXPLANATION FOR THE TECHNICAL REPORT:
1. Why the encoding scheme was used:
   After AES encrypts our data, the resulting output is raw binary (bytes). These bytes are often non-printable and can contain control characters (like Null bytes or EOF characters). If we send raw bytes directly over a network socket, especially in a text-based chat application, it can cause the socket to crash, prematurely terminate, or corrupt the data. We use Hexadecimal encoding to convert these dangerous raw bytes into safe, printable ASCII characters (0-9, A-F) that can be easily transmitted.

2. Where it was used in the system:
   The encoding scheme is applied at the very end of the encryption workflow (after AES-CBC has produced the final ciphertext bytes) but before the data is sent over the network. Conversely, on the receiving end, the incoming text must be decoded from Hexadecimal back to raw bytes before it can be fed into the AES decryption function.

3. How encrypted binary data is converted into transferable/displayable format:
   Hexadecimal encoding works by taking each byte of the encrypted data (which consists of 8 bits) and splitting it into two 4-bit segments (nibbles). Each 4-bit segment is then mapped to a corresponding character in the set '0123456789ABCDEF'. This ensures that 1 raw byte becomes exactly 2 safe text characters, making the entire ciphertext safe to display in the UI and transmit over sockets.

CRITICAL RULE: No built-in .hex() or binascii functions are used here.
Everything is built completely from scratch using bitwise operations.
"""

# Hardcoded lookup tables to avoid any built-in hex libraries
HEX_CHARS = "0123456789ABCDEF"
HEX_MAP = {char: index for index, char in enumerate(HEX_CHARS)}

def manual_hex_encode(data_bytes):
    """
    Manually encodes a bytes object into a Hexadecimal string.
    Does not use Python's built in .hex() method.
    """
    hex_string = ""
    for byte in data_bytes:
        # Get the top 4 bits (shift right by 4)
        high_nibble = (byte >> 4) & 0x0F
        # Get the bottom 4 bits (mask with 00001111)
        low_nibble = byte & 0x0F
        
        # Map to our custom character set
        hex_string += HEX_CHARS[high_nibble]
        hex_string += HEX_CHARS[low_nibble]
        
    return hex_string

def manual_hex_decode(hex_string):
    """
    Manually decodes a Hexadecimal string back into a bytes object.
    Does not use built-in bytes.fromhex() method.
    """
    if len(hex_string) % 2 != 0:
        raise ValueError("Hex string must have an even number of characters.")
    
    hex_string = hex_string.upper()
    byte_array = bytearray()
    
    for i in range(0, len(hex_string), 2):
        high_char = hex_string[i]
        low_char = hex_string[i+1]
        
        if high_char not in HEX_MAP or low_char not in HEX_MAP:
            raise ValueError(f"Invalid hex character encountered: {high_char}{low_char}")
            
        high_nibble = HEX_MAP[high_char]
        low_nibble = HEX_MAP[low_char]
        
        # Shift the high nibble back to the top 4 bits and combine with low nibble
        byte_val = (high_nibble << 4) | low_nibble
        byte_array.append(byte_val)
        
    return bytes(byte_array)
