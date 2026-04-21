import time

import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings as s


# sign in
def sign_in_jwt(user_id: int) -> dict[str, str]:
    expiration_time = time.time() + s.access_token_expire_minutes * 60
    payload = {"user_id": user_id, "exp": expiration_time}
    token = jwt.encode(payload, s.secret_key.get_secret_value(), algorithm=s.algorithm)
    return {"access_token": token}


def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, s.secret_key.get_secret_value(), algorithms=[s.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> str:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        # credentials will contain the scheme and the credentials
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or not credentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Invalid or missing authentication token")

        # decoded_token will contain the token payload
        decoded_token = decode_jwt(credentials.credentials)

        # Returns the user_id from the token payload
        return decoded_token.get("user_id")
