from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Hash import SHA256

from xint_sdk.interactsh import InteractCreds


def test_creds():
    creds = InteractCreds.new()
    encryptor = PKCS1_OAEP.new(creds.private_key.public_key(), hashAlgo=SHA256)
    decryptor = PKCS1_OAEP.new(creds.private_key, hashAlgo=SHA256)
    msg = b"this is a round trip test of encryption"
    assert msg == decryptor.decrypt(encryptor.encrypt(msg))
