#note: the S and I_S Box, mix and I_mix columns were implemented fully using ai due their complexity and many errors when attemepted manually as shown if the commented version of the mix column is used.
#other parts of the code were fixed or cleaned using ai however were majorly written by the team. the code has been tested and works correctly.
#note: this code uses aes128 with pkcs7 padding and uses ecb mode.

S_BOX = [
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5,
    0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0,
    0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC,
    0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A,
    0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0,
    0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B,
    0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85,
    0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5,
    0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17,
    0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88,
    0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C,
    0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9,
    0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6,
    0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E,
    0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94,
    0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68,
    0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
]

INV_S_BOX = [
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
]



round_keys = []

Rc = [
    0x01,
    0x02,
    0x04,
    0x08,
    0x10,
    0x20,
    0x40,
    0x80,
    0x1B,
    0x36
]


def sub_byte(byte):
    return S_BOX[byte]


def I_sub_byte(byte):
    return INV_S_BOX[byte]


def pad(data):
	pad_len = 16 - (len(data) % 16)
	padding = bytes([pad_len] * pad_len)
	return data + padding


def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def split(data):
	return [data[i:i+16] for i in range(0, len(data), 16)] 

def pre_encrypt(block, key_bytes):
    return bytes([b ^ key_bytes[i] for i, b in enumerate(block)])

def pre_decrypt(block, key_bytes):
    return bytes([b ^ key_bytes[i] for i, b in enumerate(block)])

def key_rounds(key):
	key = key.replace(" ","")
	key_bytes = bytes.fromhex(key)
	t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16 = key_bytes
	for i in range(10):
		w1 = (t1 << 24) | (t2 << 16) | (t3 << 8) | t4
		w2 = (t5 << 24) | (t6 << 16) | (t7 << 8) | t8
		w3 = (t9 << 24) | (t10 << 16) | (t11 << 8) | t12
		w4 = (t13 << 24) | (t14 << 16) | (t15 << 8) | t16
		rot = ((w4 << 8 & 0xffffffff) | w4 >> 24)
		x1 = (rot >> 24) & 0xff
		x2 = (rot >> 16) & 0xff
		x3 = (rot >> 8) & 0xff
		x4 = rot & 0xff
		s1 = sub_byte(x1)
		s2 = sub_byte(x2)
		s3 = sub_byte(x3)
		s4 = sub_byte(x4)
		s1 ^= Rc[i]
		recomb = (s1 << 24) | (s2 << 16) | (s3 << 8) | s4
		w5 = recomb ^ w1
		w6 = w5 ^ w2
		w7 = w6 ^ w3
		w8 = w7 ^ w4
		round_keys.append([w5, w6, w7, w8])
		t1  = (w5 >> 24) & 0xff
		t2  = (w5 >> 16) & 0xff
		t3  = (w5 >> 8) & 0xff
		t4  = w5 & 0xff
		t5  = (w6 >> 24) & 0xff
		t6  = (w6 >> 16) & 0xff
		t7  = (w6 >> 8) & 0xff
		t8  = w6 & 0xff
		t9  = (w7 >> 24) & 0xff
		t10 = (w7 >> 16) & 0xff
		t11 = (w7 >> 8) & 0xff
		t12 = w7 & 0xff
		t13 = (w8 >> 24) & 0xff
		t14 = (w8 >> 16) & 0xff
		t15 = (w8 >> 8) & 0xff
		t16 = w8 & 0xff
	return round_keys


def xtime(x):
    x <<= 1
    if x & 0x100:
        x ^= 0x1b
    return x & 0xff


def mul2(x):
    return xtime(x)

def mul3(x):
    return xtime(x) ^ x


def mul9(x):
    return xtime(xtime(xtime(x))) ^ x

def mul11(x):
    return xtime(xtime(xtime(x))) ^ xtime(x) ^ x

def mul13(x):
    return xtime(xtime(xtime(x))) ^ xtime(xtime(x)) ^ x

def mul14(x):
    return xtime(xtime(xtime(x))) ^ xtime(xtime(x)) ^ xtime(x)


def mix_columns_enc(block):
    block = bytearray(block)

    for i in range(4):
        a0 = block[i]
        a1 = block[i + 4]
        a2 = block[i + 8]
        a3 = block[i + 12]

        block[i]      = mul2(a0) ^ mul3(a1) ^ a2 ^ a3
        block[i + 4]  = a0 ^ mul2(a1) ^ mul3(a2) ^ a3
        block[i + 8]  = a0 ^ a1 ^ mul2(a2) ^ mul3(a3)
        block[i + 12] = mul3(a0) ^ a1 ^ a2 ^ mul2(a3)

    return bytes(block)

def mix_columns_dec(block):
    block = bytearray(block)

    for i in range(4):
        a0 = block[i]
        a1 = block[i + 4]
        a2 = block[i + 8]
        a3 = block[i + 12]

        block[i]      = mul14(a0) ^ mul11(a1) ^ mul13(a2) ^ mul9(a3)
        block[i + 4]  = mul9(a0) ^ mul14(a1) ^ mul11(a2) ^ mul13(a3)
        block[i + 8]  = mul13(a0) ^ mul9(a1) ^ mul14(a2) ^ mul11(a3)
        block[i + 12] = mul11(a0) ^ mul13(a1) ^ mul9(a2) ^ mul14(a3)

    return bytes(block)


# def mix_columns(block):
#     temp  = bytearray(block)
#     temp1 = bytearray(block)
#     temp2 = bytearray(block)
#     temp3 = bytearray(block)
#     temp4 = bytearray(block)

#     temp1[0] = temp1[0] << 1
#     if temp1[0] >= 0x80:
#             temp1[0] ^= 0x1b
#             temp1[0] &= 0xff
#     temp1[1] = temp1[1] << 1
#     if temp1[1] >= 0x80:
#         temp1[1] ^= 0x1b
#         temp1[1] &= 0xff
#         temp1[1] ^= temp[1]
    
#     s0 =  temp1[0] ^ temp1[1] ^ temp1[2] ^ temp1[3]

#     temp1[4] = temp1[4] << 1
#     if temp1[4] >= 0x80:
#             temp1[4] ^= 0x1b
#             temp1[4] &= 0xff
#     temp1[5] = temp1[5] << 1
#     if temp1[5] >= 0x80:
#         temp1[5] ^= 0x1b
#         temp1[5] &= 0xff
#         temp1[5] ^= temp[5]
    
#     s1 =  temp1[4] ^ temp1[5] ^ temp1[6] ^ temp1[7]

#     temp1[8] = temp1[8] << 1
#     if temp1[8] >= 0x80:
#             temp1[8] ^= 0x1b
#             temp1[8] &= 0xff
#     temp1[9] = temp1[9] << 1
#     if temp1[9] >= 0x80:
#         temp1[9] ^= 0x1b
#         temp1[9] &= 0xff
#         temp1[9] ^= temp[9]
    
#     s2 =  temp1[8] ^ temp1[9] ^ temp1[10] ^ temp1[11]

#     temp1[12] = temp1[12] << 1
#     if temp1[12] >= 0x80:
#             temp1[12] ^= 0x1b
#             temp1[12] &= 0xff
#     temp1[13] = temp1[13] << 1
#     if temp1[13] >= 0x80:
#         temp1[13] ^= 0x1b
#         temp1[13] &= 0xff
#         temp1[13] ^= temp[13]
    
#     s3 =  temp1[12] ^ temp1[13] ^ temp1[14] ^ temp1[15]

#     temp2[1] = temp2[1] << 1
#     if temp2[1] >= 0x80:
#             temp2[1] ^= 0x1b
#             temp2[1] &= 0xff
#     temp2[2] = temp2[2] << 1
#     if temp2[2] >= 0x80:
#         temp2[2] ^= 0x1b
#         temp2[2] &= 0xff
#         temp2[2] ^= temp[2]
    
#     s4 = temp2[0] ^ temp2[1] ^ temp2[2] ^ temp2[3]

#     temp2[5] = temp2[5] << 1
#     if temp2[5] >= 0x80:
#             temp2[5] ^= 0x1b
#             temp2[5] &= 0xff
#     temp2[6] = temp2[6] << 1
#     if temp2[6] >= 0x80:
#         temp2[6] ^= 0x1b
#         temp2[6] &= 0xff
#         temp2[6] ^= temp[6]
    
#     s5 = temp2[4] ^ temp2[5] ^ temp2[6] ^ temp2[7]

#     temp2[9] = temp2[9] << 1
#     if temp2[9] >= 0x80:
#             temp2[9] ^= 0x1b
#             temp2[9] &= 0xff
#     temp2[10] = temp2[10] << 1
#     if temp2[10] >= 0x80:
#         temp2[10] ^= 0x1b
#         temp2[10] &= 0xff
#         temp2[10] ^= temp[10]
    
#     s6 = temp2[8] ^ temp2[9] ^ temp2[10] ^ temp2[11]

#     temp2[13] = temp2[13] << 1
#     if temp2[13] >= 0x80:
#             temp2[13] ^= 0x1b
#             temp2[13] &= 0xff
#     temp2[14] = temp2[14] << 1
#     if temp2[14] >= 0x80:
#         temp2[14] ^= 0x1b
#         temp2[14] &= 0xff
#         temp2[14] ^= temp[14]
    
#     s7 = temp2[12] ^ temp2[13] ^ temp2[14] ^ temp2[15]

#     temp3[2] = temp3[2] << 1
#     if temp3[2] >= 0x80:
#             temp3[2] ^= 0x1b
#             temp3[2] &= 0xff
#     temp3[3] = temp3[3] << 1
#     if temp3[3] >= 0x80:
#         temp3[3] ^= 0x1b
#         temp3[3] &= 0xff
#         temp3[3] ^= temp[3]
    
#     s8 = temp3[0] ^ temp3[1] ^ temp3[2] ^ temp3[3]
                                                
#     temp3[6] = temp3[6] << 1
#     if temp3[6] >= 0x80:
#             temp3[6] ^= 0x1b
#             temp3[6] &= 0xff
#     temp3[7] = temp3[7] << 1
#     if temp3[7] >= 0x80:
#         temp3[7] ^= 0x1b
#         temp3[7] &= 0xff
#         temp3[7] ^= temp[7]
    
#     s9 = temp3[4] ^ temp3[5] ^ temp3[6] ^ temp3[7]


#     temp3[10] = temp3[10] << 1
#     if temp3[10] >= 0x80:
#             temp3[10] ^= 0x1b
#             temp3[10] &= 0xff
#     temp3[11] = temp3[11] << 1
#     if temp3[11] >= 0x80:
#         temp3[11] ^= 0x1b
#         temp3[11] &= 0xff
#         temp3[11] ^= temp[11]
    
#     s10 = temp3[8] ^ temp3[9] ^ temp3[10] ^ temp3[11]
    

#     temp3[14] = temp3[14] << 1
#     if temp3[14] >= 0x80:
#             temp3[14] ^= 0x1b
#             temp3[14] &= 0xff
#     temp3[15] = temp3[15] << 1
#     if temp3[15] >= 0x80:
#         temp3[15] ^= 0x1b
#         temp3[15] &= 0xff
#         temp3[15] ^= temp[15]
    
#     s11 = temp3[12] ^ temp3[13] ^ temp3[14] ^ temp3[15]

#     temp4[0] = temp4[0] << 1
#     if temp4[0] >= 0x80:
#         temp4[0] ^= 0x1b
#         temp4[0] &= 0xff
#         temp4[0] ^= temp[0]
#     temp4[3] = temp4[3] << 1
#     if temp4[3] >= 0x80:
#             temp4[3] ^= 0x1b
#             temp4[3] &= 0xff

#     s12 = temp4[0] ^ temp4[1] ^ temp4[2] ^ temp4[3]

#     temp4[4] = temp4[4] << 1
#     if temp4[4] >= 0x80:
#         temp4[4] ^= 0x1b
#         temp4[4] &= 0xff
#         temp4[4] ^= temp[4]
#     temp4[7] = temp4[7] << 1
#     if temp4[7] >= 0x80:
#             temp4[7] ^= 0x1b
#             temp4[7] &= 0xff
            
#     s13 = temp4[4] ^ temp4[5] ^ temp4[6] ^ temp4[7]


#     temp4[8] = temp4[8] << 1
#     if temp4[8] >= 0x80:
#         temp4[8] ^= 0x1b
#         temp4[8] &= 0xff
#         temp4[8] ^= temp[8]
#     temp4[11] = temp4[11] << 1
#     if temp4[11] >= 0x80:
#             temp4[11] ^= 0x1b
#             temp4[11] &= 0xff
            
#     s14 = temp4[8] ^ temp4[9] ^ temp4[10] ^ temp4[11]

#     temp4[12] = temp4[12] << 1
#     if temp4[12] >= 0x80:
#         temp4[12] ^= 0x1b
#         temp4[12] &= 0xff
#         temp4[12] ^= temp[12]
#     temp4[15] = temp4[15] << 1
#     if temp4[15] >= 0x80:
#             temp4[15] ^= 0x1b
#             temp4[15] &= 0xff
            
#     s15 = temp4[12] ^ temp4[13] ^ temp4[14] ^ temp4[15]

#     return bytes([s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15])



def aes_rounds_dec(block):
    for i in range(9):
        block = bytes([I_sub_byte(b) for b in block])

        block = bytearray(block)
        block[1], block[5], block[9], block[13] = block[13], block[1], block[5], block[9]
        block[2], block[6], block[10], block[14] = block[10], block[14], block[2], block[6]
        block[3], block[7], block[11], block[15] = block[7], block[11], block[15], block[3]
        
        block = mix_columns_dec(block)

        round_key = round_keys[9 - i - 1]
        rk = []

        for word in round_key:
            rk.extend([
            (word >> 24) & 0xff,
            (word >> 16) & 0xff,
            (word >> 8) & 0xff,
            word & 0xff
            ])

        for j in range(16):
            block[j] ^= rk[j]

    return bytearray([b & 0xff for b in block])

    		
    
def aes_rounds_enc(block):
    for i in range(9):
        # Substitute bytes
        block = bytes([sub_byte(b) for b in block])

        # Shift rows
        block = bytearray(block)
        block[1], block[5], block[9], block[13] = block[5], block[9], block[13], block[1]
        block[2], block[6], block[10], block[14] = block[10], block[14], block[2], block[6]
        block[3], block[7], block[11], block[15] = block[15], block[3], block[7], block[11]

        # Mix columns
        block = mix_columns_enc(block)
        block = bytearray(block)
        
        # Add round key
        round_key = round_keys[i]
        rk = []
        for word in round_key:
            rk.extend([
            (word >> 24) & 0xff,
            (word >> 16) & 0xff,
            (word >> 8) & 0xff,
            word & 0xff
            ])

        for j in range(16):
            block[j] ^= rk[j]

    return bytearray([b & 0xff for b in block])


def final_round_enc(block):

    block = bytes([sub_byte(b) for b in block])
    
    block = bytearray(block)
    block[1], block[5], block[9], block[13] = block[5], block[9], block[13], block[1]
    block[2], block[6], block[10], block[14] = block[10], block[14], block[2], block[6]
    block[3], block[7], block[11], block[15] = block[15], block[3], block[7], block[11]

    round_key = round_keys[9]
    rk = []

    for word in round_key:
        rk.extend([
        (word >> 24) & 0xff,
        (word >> 16) & 0xff,
        (word >> 8) & 0xff,
        word & 0xff
        ])

    for j in range(16):
        block[j] ^= rk[j]

    return bytearray([b & 0xff for b in block]) #fixed using ai

def aes_encrypt(plain, key):
    round_keys.clear()
    key_bytes = bytes.fromhex(key.replace(" ", ""))
    if len(key_bytes) != 16:
        raise ValueError("Key must be exactly 16 bytes (32 hex characters)")
    key_rounds(key)
    plain_bytes = plain.encode()
    padded = pad(plain_bytes)
    blocks = split(padded)
    ciphertext = b""
    for block in blocks:
        pre = pre_encrypt(block, key_bytes)
        rounds_1_9 = aes_rounds_enc(pre)
        final_block = final_round_enc(rounds_1_9)
        ciphertext += bytes(final_block)
    return ciphertext


def aes_decrypt(ciphertext, key):
    round_keys.clear()

    key_bytes = bytes.fromhex(key.replace(" ", ""))
    if len(key_bytes) != 16:
        raise ValueError("Key must be exactly 16 bytes")

    key_rounds(key)

    ciphertext_bytes = bytes.fromhex(ciphertext.replace(" ", ""))
    blocks = split(ciphertext_bytes)

    plaintext = b""

    all_round_keys = []

    for rk_words in round_keys:
        rk = []
        for word in rk_words:
            rk.extend([
                (word >> 24) & 0xff,
                (word >> 16) & 0xff,
                (word >> 8) & 0xff,
                word & 0xff
            ])
        all_round_keys.append(bytes(rk))

    for block in blocks:

        block = bytearray(block)

        for i in range(16):
            block[i] ^= all_round_keys[9][i]

        block[1], block[5], block[9], block[13] = block[13], block[1], block[5], block[9]
        block[2], block[6], block[10], block[14] = block[10], block[14], block[2], block[6]
        block[3], block[7], block[11], block[15] = block[7], block[11], block[15], block[3]

        block = bytearray([I_sub_byte(b) for b in block])

        for r in range(8, -1, -1):

            for i in range(16):
                block[i] ^= all_round_keys[r][i]

            block = bytearray(mix_columns_dec(block))

            block[1], block[5], block[9], block[13] = block[13], block[1], block[5], block[9]
            block[2], block[6], block[10], block[14] = block[10], block[14], block[2], block[6]
            block[3], block[7], block[11], block[15] = block[7], block[11], block[15], block[3]

            block = bytearray([I_sub_byte(b) for b in block])

        for i in range(16):
            block[i] ^= key_bytes[i]

        plaintext += bytes(block)

    plaintext = unpad(plaintext)

    return plaintext.decode()


def encrypt():
    plain = input("please input plaintext ")
    key = input("please input key ")
    try:
        ciphertext = aes_encrypt(plain, key)
        print("ciphertext:", ciphertext.hex())
        # decrypted = aes_decrypt(ciphertext.hex(), key)
        # print("decrypted:", decrypted)
    except ValueError as err:
        print("Invalid key:", err)

def decrypt():
    ciphertext = input("please input ciphertext ")
    key = input("please input key ")
    try:
        plaintext = aes_decrypt(ciphertext, key)
        print("plaintext:", plaintext)
    except ValueError as err:
        print("Invalid key or ciphertext:", err)

if __name__ == "__main__":
    choice = input("Enter 1 to encrypt, 2 to decrypt: ")
    if choice == "1":
        encrypt()
    elif choice == "2":    
        decrypt()
    else:
        print("Invalid choice. Please enter 1 or 2.")
