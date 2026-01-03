from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def normalize_password(password: str) -> str:
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

password = "nandytamvan11"
hashed = pwd_context.hash(normalize_password(password))
print(hashed)
