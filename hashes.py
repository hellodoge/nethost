from __future__ import annotations
from hashlib    import sha256


class Hash:

    def __init__(self, text: str):
        hash_obj = sha256(text.encode('utf-8'))
        self.__hash = hash_obj.digest().hex()

    def __eq__(self, other: Hash) -> bool:
        return self.__hash == other.__hash

    def __repr__(self) -> str:
        return self.__hash[:8]

    def save(self) -> str:
        return self.__hash

    @staticmethod
    def load(serialized: str):
        hash_sum = Hash('')
        hash_sum.__hash = serialized
        return hash_sum
