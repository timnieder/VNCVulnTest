import pyDes # pyDes.py

class RFBDes(pyDes.des):
    def setKey(self, key: bytes) -> None:
        """RFB protocol for authentication requires client to encrypt
           challenge sent by server with password using DES method. However,
           bits in each byte of the password are put in reverse order before
           using it as encryption key."""
        newkey = bytes(
            sum((128 >> i) if (k & (1 << i)) else 0 for i in range(8))
            for k in key
        )
        super().setKey(newkey)