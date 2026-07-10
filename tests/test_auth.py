from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.vehicles import router as vehicles_router
from app.config import settings
from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_database

#Base de datos falsa

@pytest.fixture
def fake_database():

    return {
        "users": MagicMock(),
        "vehicles": MagicMock(),
    }

#App FastAPI falsa

@pytest.fixture
def client(fake_database):

    test_app = FastAPI()

    test_app.include_router(auth_router)
    test_app.include_router(vehicles_router)

    def override_get_database():
        return fake_database

    test_app.dependency_overrides[get_database] = override_get_database

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()


class TestPasswordSecurity:

    def test_hash_and_verify_password_roundtrip(self):
        plain_password = "secret123"

        hashed_password = hash_password(plain_password)

        assert hashed_password != plain_password
        assert verify_password(plain_password, hashed_password)
        assert not verify_password("otra-contraseña", hashed_password)


class TestAccessToken:

    def test_create_access_token_contains_user_and_expiration(self):
        email = "admin@miniflota.com"

        token = create_access_token(
            {"sub": email}
        )

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        assert payload["sub"] == email
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_get_current_user_returns_email_for_valid_token(self):
        email = "admin@miniflota.com"

        token = create_access_token(
            {"sub": email}
        )

        current_user = await get_current_user(token)

        assert current_user == email

    @pytest.mark.asyncio
    async def test_get_current_user_raises_401_for_invalid_token(self):
        with pytest.raises(HTTPException) as error:
            await get_current_user("token-invalido")

        assert error.value.status_code == 401


class TestAuthEndpoints:

    def test_login_returns_access_token_for_valid_credentials(
        self,
        client,
        fake_database,
    ):
        plain_password = "secret123"

        fake_database["users"].find_one = AsyncMock(
            return_value={
                "email": "admin@miniflota.com",
                "hashed_password": hash_password(plain_password),
            }
        )

        response = client.post(
            "/auth/login",
            data={
                "username": "admin@miniflota.com",
                "password": plain_password,
            },
        )

        assert response.status_code == 200

        response_data = response.json()

        assert "access_token" in response_data
        assert response_data["token_type"] == "bearer"

        fake_database["users"].find_one.assert_awaited_once_with(
            {"email": "admin@miniflota.com"}
        )

    def test_login_returns_401_for_invalid_credentials(
        self,
        client,
        fake_database,
    ):
        fake_database["users"].find_one = AsyncMock(
            return_value={
                "email": "admin@miniflota.com",
                "hashed_password": hash_password("contraseña-correcta"),
            }
        )

        response = client.post(
            "/auth/login",
            data={
                "username": "admin@miniflota.com",
                "password": "contraseña-incorrecta",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

    def test_get_vehicles_returns_401_without_token(
        self,
        client,
    ):
        response = client.get("/vehicles/")

        assert response.status_code == 401