import base64
import hashlib
import hmac
import json
import time

from django.conf import settings


class JwtService:
    def __init__(self):
        self.secret = settings.JWT_SECRET.encode('utf-8')
        self.exp_minutes = settings.JWT_EXP_MINUTES

    def create_token(self, usuario):
        payload = {
            'sub': usuario.id,
            'correo': usuario.correo,
            'rol': usuario.rol,
            'compania_id': usuario.compania_id,
            'exp': int(time.time()) + (self.exp_minutes * 60),
        }
        header = {'alg': 'HS256', 'typ': 'JWT'}
        header_b64 = self._b64(json.dumps(header, separators=(',', ':')).encode())
        payload_b64 = self._b64(json.dumps(payload, separators=(',', ':')).encode())
        signature = self._sign(f'{header_b64}.{payload_b64}')
        return f'{header_b64}.{payload_b64}.{signature}'

    def decode_token(self, token: str):
        try:
            header_b64, payload_b64, signature = token.split('.')
        except ValueError:
            raise ValueError('Token invalido')

        expected = self._sign(f'{header_b64}.{payload_b64}')
        if not hmac.compare_digest(signature, expected):
            raise ValueError('Firma JWT invalida')

        payload = json.loads(self._unb64(payload_b64))
        if payload['exp'] < int(time.time()):
            raise ValueError('Token expirado')
        return payload

    def _sign(self, value: str) -> str:
        digest = hmac.new(self.secret, value.encode('utf-8'), hashlib.sha256).digest()
        return self._b64(digest)

    def _b64(self, value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b'=').decode('ascii')

    def _unb64(self, value: str) -> bytes:
        padding = '=' * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
