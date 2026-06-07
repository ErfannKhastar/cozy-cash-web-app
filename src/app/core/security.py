"""
Security and Hashing Utilities.

This module provides functions for hashing passwords and verifying them against
stored hashes using the bcrypt algorithm. It acts as a wrapper around the `passlib` library.
"""

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
