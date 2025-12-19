import base64
import json
import os
import time
import uuid

import requests
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Hash import HMAC, SHA256
from Cryptodome.PublicKey import RSA

SERVER_DOMAIN = "xintbot.link"

RESP_WAIT_TIMEOUT = 15
RESP_WAIT_EXTENSION = 2
RESP_WAIT_ITER = 0.1


def random_id(sz) -> str:
    return base64.b32encode(os.urandom(sz)).decode("utf-8").lower()[:sz]


class DRBG:
    def __init__(self, seed: bytes):
        self.seed = bytes(seed)
        self.label = b"rsa-keygen"
        self.counter = 0

    def __call__(self, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            ctr = self.counter.to_bytes(8, byteorder="big")
            block = HMAC.new(self.seed, self.label + ctr, digestmod=SHA256).digest()
            out.extend(block)
            self.counter += 1
        return bytes(out[:n])


class InteractCreds:
    def __init__(self, sh_key: str, keyphrase: str, corr_id: str):
        self.sh_key = sh_key
        self.keyphrase = keyphrase
        self.private_key = RSA.generate(2048, DRBG(keyphrase.encode()))
        self.corr_id = corr_id

    @classmethod
    def new(cls) -> "InteractCreds":
        return cls(sh_key=str(uuid.uuid4()), keyphrase=random_id(24), corr_id=random_id(20))

    def domain(self) -> str:
        nonce = random_id(13)
        return f"{self.corr_id}{nonce}.{SERVER_DOMAIN}"

    def export(self) -> str:
        return f"InteractCreds(sh_key={self.sh_key!r}, keyphrase={self.keyphrase!r}, corr_id={self.corr_id!r})"


class InteractshPrivate:
    def __init__(self, creds: InteractCreds, auth_token: str):
        self.creds = creds
        self.auth_token = auth_token

    def register(self) -> None:
        registration_data = {
            "correlation-id": self.creds.corr_id,
            "public-key": base64.b64encode(self.creds.private_key.public_key().export_key()).decode("utf-8"),
            "secret-key": self.creds.sh_key,
        }
        r = requests.post(
            f"https://{SERVER_DOMAIN}/register",
            headers={"Authorization": self.auth_token},
            json=registration_data,
        )
        r.raise_for_status()
        response = r.json()
        assert response["message"] == "registration successful"

    def deregister(self) -> None:
        r = requests.post(
            f"https://{SERVER_DOMAIN}/deregister",
            headers={"Authorization": self.auth_token},
            json={
                "correlation-id": self.creds.corr_id,
                "secret-key": self.creds.sh_key,
            },
        )
        r.raise_for_status()


class Interactsh:
    def __init__(self, creds: InteractCreds):
        self.creds = creds

    def domain(self) -> str:
        return self.creds.domain()

    def wait_for_response(self) -> list[dict[str, str]]:
        deadline = time.monotonic() + RESP_WAIT_TIMEOUT
        terminating = False
        res = []
        while time.monotonic() < deadline:
            res.extend(self._poll())
            if res and not terminating:
                deadline = time.monotonic() + RESP_WAIT_EXTENSION
                terminating = True
            time.sleep(RESP_WAIT_ITER)
        return res

    def _poll(self) -> list[dict[str, str]]:
        r = requests.get(
            f"https://{SERVER_DOMAIN}/poll",
            params={
                "id": self.creds.corr_id,
                "secret": self.creds.sh_key,
            },
        )
        r.raise_for_status()
        response = r.json()
        return [
            *[json.loads(self._decrypt(response["aes_key"], d)) for d in response.get("data") or []],
            *[json.loads(d) for d in response.get("extra") or []],
        ]

    def _decrypt(self, encrypted_aes_key_b64: str, data_b64: str) -> str:
        encrypted_aes_key = base64.b64decode(encrypted_aes_key_b64)
        data = base64.b64decode(data_b64)

        decryptor = PKCS1_OAEP.new(self.creds.private_key, hashAlgo=SHA256)
        aes_key = decryptor.decrypt(encrypted_aes_key)

        iv = data[:16]
        ciphertext = data[16:]

        cipher = AES.new(aes_key, AES.MODE_CFB, iv=iv, segment_size=128)
        plaintext = cipher.decrypt(ciphertext)

        return plaintext.decode("utf-8")
