import os
from cryptography.fernet import Fernet

key = os.getenv("FERNET_KEY")

if not key:
    raise ValueError("FERNET_KEY not found in environment variables")

cipher = Fernet(key.encode())

def encrypt_text(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(text):
  return cipher.decrypt(text.encode()).decode()