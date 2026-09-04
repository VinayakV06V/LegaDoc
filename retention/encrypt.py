from cryptography.fernet import Fernet
import os

KEY_PATH = os.path.join("retention", "secret.key")

def generate_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)

def load_key():
    with open(KEY_PATH, "rb") as f:
        return f.read()

def encrypt_text(text):
    if text is None:
        return None

    cipher = Fernet(load_key())
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(text):
    if text is None:
        return None

    cipher = Fernet(load_key())
    return cipher.decrypt(text.encode()).decode()

generate_key()