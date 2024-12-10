from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes  # Added hashes import
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

# Generate a secure AES secret key if not set in the environment
AES_SECRET_KEY = "r05XA0HdmdEFYVDPyrkJ7wLqs-fkUMAyLX09tXlIiVs="


# Salt should be saved with the ciphertext for later key derivation
SALT = os.urandom(16)

def get_key_from_password(password: str, salt: bytes) -> bytes:
    """ Derive a key from the password using PBKDF2 """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),  # Use SHA-256 hashing
        length=32,  # AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_message(message: str) -> str:
    """ Encrypts a message using AES encryption (CBC mode). """
    salt = os.urandom(16)  # Generate a new salt for each message
    key = get_key_from_password(AES_SECRET_KEY, salt)
    iv = os.urandom(16)  # Random IV for each encryption
    
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

    # Combine salt, IV, and encrypted message into one data
    encrypted_message_base64 = base64.b64encode(salt + iv + encrypted_message).decode('utf-8')
    return encrypted_message_base64

def decrypt_message(encrypted_message_base64: str) -> str:
    """ Decrypts a message using AES decryption (CBC mode). """
    encrypted_data = base64.b64decode(encrypted_message_base64)
    
    salt = encrypted_data[:16]  # Extract the salt
    iv = encrypted_data[16:32]  # Extract the IV
    encrypted_message = encrypted_data[32:]  # Extract the actual encrypted message

    key = get_key_from_password(AES_SECRET_KEY, salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_message_padded = decryptor.update(encrypted_message) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_message = unpadder.update(decrypted_message_padded) + unpadder.finalize()
    
    return decrypted_message.decode('utf-8')

