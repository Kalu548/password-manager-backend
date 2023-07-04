import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

hardcodedIV = bytes([
    0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb,
    0xcc, 0xdd, 0xee, 0xff,
])


def return_decrypted_password(password, master_key):
    key_data = master_key.encode('utf-8')
    cipher = AES.new(key_data, AES.MODE_CBC, hardcodedIV)
    encrypted_data = base64.b64decode(password)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    decrypted = decrypted_data.decode('utf-8')
    return decrypted
