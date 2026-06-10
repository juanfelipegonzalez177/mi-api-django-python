from django.contrib.auth.hashers import check_password, make_password


class PasswordHasher:
    def hash(self, password: str) -> str:
        return make_password(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return check_password(password, password_hash)
