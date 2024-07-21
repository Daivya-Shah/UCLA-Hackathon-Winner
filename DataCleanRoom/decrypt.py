# NOTE
# THIS CODE IS A MODIFICATION OF CODE PROVIDED BY Trustworthy AI Lab x GES UCLA Hackathon

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64


def unpad(data):
    padding_length = data[-1]
    return data[:-padding_length]

def pad(data):
    padding_length = 16 - len(data) % 16
    return data + bytes([padding_length]) * padding_length

def encrypt_aes(data, key):
    key = key[:32].ljust(32, b'\0')
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data)
    encrypted_data = cipher.encrypt(padded_data)
    return iv + encrypted_data

def decrypt_aes(encrypted_data, key):
    key = key[:32].ljust(32, b'\0')
    iv = encrypted_data[:16]  # Extract the IV
    encrypted_data = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_data)
    return unpad(decrypted_data)


def read_file(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def write_binary_file(file_path, data):
    with open(file_path, 'wb') as file:
        file.write(data)



# Example usage
key = b'functionremainsunchangedasitwillcorrectly'  # Your encryption key
input_file_path = 'train.zip'  # Path to the input binary file
encrypted_file_path = 'train.bin'  # Path to the output encrypted file
decrypted_file_path = 'decrypted_file.zip'  # Path to the output decrypted file


def decrypt(encrypted_file_path, key, decrypted_file_path):
    # Read the encrypted data from the encrypted file
    encrypted_data_from_file = read_file(encrypted_file_path)

    # Decrypt the data and write it to the decrypted file
    decrypted_data = decrypt_aes(encrypted_data_from_file, key)
    write_binary_file(decrypted_file_path, decrypted_data)

    print('decryption completed successfully.')

def encrypt(decrypted_file_path,):
    # Encrypt the data and write it to the encrypted file
    data_to_encrypt = read_file(decrypted_file_path)
    encrypted_data = encrypt_aes(data_to_encrypt, key)
    write_binary_file(encrypted_file_path, encrypted_data)

    print('encryption completed successfully.')
