from abc import ABC, abstractmethod
import binascii
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util import Counter
import json
from typing import Tuple

#Returns iv and decrypted text, both are 'bytes' objects
def encrypt(key: bytes, plaintext: bytes) -> Tuple[bytes, bytes]:
    assert len(key) == 32, "Only accepts 32-byte keys"

    # Choose a random, 16-byte IV.
    iv = Random.new().read(AES.block_size)
    # Convert the IV to a Python integer.
    iv_int = int(binascii.hexlify(iv), 16)
    # Create a new Counter object with IV = iv_int.
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)
    # Encrypt and return IV and ciphertext.
    ciphertext = aes.encrypt(plaintext)
    return (iv, ciphertext)

#Takes iv and decrypted text as inputs ('bytes' objects), returns encrypted text.
def decrypt(key: bytes, iv: bytes, ciphertext: bytes):
    # Initialize counter for decryption. iv should be the same as the output of
    # encrypt().
    iv_int = int.from_bytes(iv, "big")
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)
    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)
    # Decrypt and return the plaintext.
    plaintext = aes.decrypt(ciphertext)
    return plaintext.decode("utf-8")

def decrypt_json(key: str, obj: dict) -> dict:
    if ("iv" in obj) and ("content" in obj):
        return json.loads(decrypt(key.encode("utf-8"), bytes.fromhex(obj["iv"]),
                                    bytes.fromhex(obj["content"])))
    return obj

def encrypt_json(key: str, obj: dict) -> dict:
    iv, content = encrypt(key.encode("utf-8"), json.dumps(obj).encode("utf-8"))
    return {
        "iv": iv.hex(),
        "content": content.hex()
    }


class Reader(ABC):
    @abstractmethod
    def read(self, filepath: str) -> str:
        pass

    @abstractmethod
    def write(self, content: str, filepath: str) -> None:
        pass

class TextReader(Reader):
    def read(self, filepath: str) -> str:
        with open(filepath, "r") as fopen:
            return fopen.read()

    def write(self, content: str, filepath: str) -> None:
        with open(filepath, "w") as fopen:
            fopen.write(content)

class EncryptedTextReader(Reader):
    def __init__(self, encrypt_key: str):
        self.__encrypt_key = encrypt_key

    def read(self, filepath: str) -> str:
        with open(filepath, "r") as fopen:
            content = json.load(fopen)

        obj = decrypt_json(self.__encrypt_key, content)
        return json.dumps(obj)

    def write(self, content: str, filepath: str) -> None:
        obj = encrypt_json(self.__encrypt_key, json.loads(content))
        with open(filepath, "w") as fopen:
            json.dump(obj, fopen)

