import bcrypt

class DataEncryption:
    def __init__(self):
        pass

    def hash_password(self, password: str) -> str:
        """Hashes a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifies a password against its hashed value."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))