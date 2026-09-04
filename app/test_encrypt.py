from retention.encrypt import encrypt_text, decrypt_text

name = "John Hawk"

encrypted = encrypt_text(name)

print("Encrypted :", encrypted)
print("Decrypted :", decrypt_text(encrypted))