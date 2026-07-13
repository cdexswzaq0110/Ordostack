import hashlib
import hmac
import secrets


def validate_password_policy(password: str, *, email: str, min_length: int) -> list[str]:
    violations: list[str] = []
    normalized_password = password.strip()
    email_local_part = email.split("@", 1)[0].strip().lower()

    if len(normalized_password) < min_length:
        violations.append(f"at least {min_length} characters")
    if not any(character.isalpha() for character in normalized_password):
        violations.append("at least one letter")
    if not any(not character.isalpha() for character in normalized_password):
        violations.append("at least one number or symbol")
    if email_local_part and email_local_part in normalized_password.lower():
        violations.append("must not contain the email username")

    return violations


# OWASP password-storage guidance for PBKDF2-HMAC-SHA256. The hash format is
# self-describing, so hashes created with older iteration counts keep verifying.
PBKDF2_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt, expected_digest = password_hash.split("$", 3)
        iterations = int(iterations_text)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations).hex()
    return hmac.compare_digest(digest, expected_digest)
