# Copyright © 2021-2026 Bull SAS
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of work done in the K-HEALTHinAIR EU funded project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# 
# 

"""
Module with AQDR API security functions.
Based on authentication scheme OAuth2 with Password and Hashing,
Bearer with JWT Tokens.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from modules.config import Config
from passlib.context import CryptContext
from pydantic import BaseModel

# Authentication scheme OAuth2
CONTEXTPATH = Config.AQDR_API_CONTEXTPATH
SECRET_KEY = Config.AQDR_API_AUTH_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=CONTEXTPATH + "/token")

# Helper context using Bcrypt hashing algorithm to hash and verify passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Contains JWT Access token returned by OAuth2PasswordRequestForm


class Token(BaseModel):
    """Token class with access_token and token_type fields."""

    access_token: str
    token_type: str


# Contains username of JWT's payload data
class TokenData(BaseModel):
    """TokenData class with username of JWT's payload data."""

    username: str | None = None


class User(BaseModel):
    """User class with username, disabled, access and description fields."""

    username: str
    disabled: bool | None = None
    access: list
    description: str


class UserInDB(User):
    """UserInDB class with hashed_password field. Inherits from User class."""

    hashed_password: str


# Security exception: invalid credentials
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_password_hash(plain_password: str) -> str:
    """Hashes provided plain password. Returns hashed password."""

    hashed_password = pwd_context.hash(plain_password)

    return hashed_password


def authenticate_user(fake_db, username: str, password: str):
    """Authenticates provided user and password from OAuth2PasswordRequestForm
    with existing users in DB, only if user exists and password is verified.
    """

    user = get_user(fake_db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    else:
        return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if provided plain password matches with existing,
    already hashed password."""

    is_verified = pwd_context.verify(plain_password, hashed_password)
    return is_verified


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates JWT access token given an authenticated username.
    Adds expiration time and encodes claims."""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_user(db, username: str):
    """Gets username from users DB."""

    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


async def get_current_user(jwt_token: Annotated[str, Depends(oauth2_scheme)]):
    """Given a JWT token, validates its signature to ensure token's integrity.
    Extracts token's payload, and then username from subject key of payload.
    If invalid signature, raises credentials exception."""

    try:
        payload = jwt.decode(jwt_token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except JWTError as exc:
        raise credentials_exception from exc

    # Searchs user from users DB, using username of the JWT Token payload
    user = get_user(api_users_db, username=token_data.username)

    if user:
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        return user
    else:
        raise credentials_exception


# Users DB, loaded from a JSON file provided at deploy time (not kept in the
# code repository). See aqdr-api-users.example.json for the expected format.
def load_api_users(users_file: str) -> dict:
    """Loads API users from a JSON file. Returns an empty DB (nobody can
    authenticate) if the file is missing or invalid."""

    try:
        with open(users_file, encoding="utf-8") as file:
            users = json.load(file)
        return {user["username"]: user for user in users}
    except (OSError, ValueError, KeyError, TypeError) as error:
        logging.error(
            "API users file [%s] couldn't be loaded: %s", users_file, error
        )
        return {}


api_users_db = load_api_users(Config.AQDR_API_USERS_FILE)
