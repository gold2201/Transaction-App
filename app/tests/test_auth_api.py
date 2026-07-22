from httpx import AsyncClient


class TestSignUp:
    async def test_success(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/sign-up",
            json={
                "email": "new@test.com",
                "full_name": "New User",
                "password": "newpass123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@test.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert data["is_admin"] is False

    async def test_duplicate_email(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/sign-up",
            json={
                "email": "dup@test.com",
                "full_name": "Dup",
                "password": "pass123",
            },
        )
        response = await client.post(
            "/auth/sign-up",
            json={
                "email": "dup@test.com",
                "full_name": "Dup2",
                "password": "pass456",
            },
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_invalid_email(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/sign-up",
            json={
                "email": "notanemail",
                "full_name": "Bad",
                "password": "pass123",
            },
        )
        assert response.status_code == 422

    async def test_short_password(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/sign-up",
            json={
                "email": "short@test.com",
                "full_name": "Short",
                "password": "12345",
            },
        )
        assert response.status_code == 422


class TestSignIn:
    async def test_success(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/sign-up",
            json={
                "email": "login@test.com",
                "full_name": "Login",
                "password": "pass123",
            },
        )
        response = await client.post(
            "/auth/sign-in",
            data={
                "username": "login@test.com",
                "password": "pass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_wrong_password(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/sign-up",
            json={
                "email": "wrong@test.com",
                "full_name": "Wrong",
                "password": "pass123",
            },
        )
        response = await client.post(
            "/auth/sign-in",
            data={
                "username": "wrong@test.com",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 401

    async def test_nonexistent_user(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/sign-in",
            data={
                "username": "nobody@test.com",
                "password": "pass123",
            },
        )
        assert response.status_code == 401


class TestRefresh:
    async def test_invalid_token(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/refresh",
            json={
                "refresh_token": "invalid_token_here",
            },
        )
        assert response.status_code == 401


class TestLogout:
    async def test_success(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/sign-up",
            json={
                "email": "logout@test.com",
                "full_name": "Logout",
                "password": "pass123",
            },
        )
        login_resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "logout@test.com",
                "password": "pass123",
            },
        )
        access_token = login_resp.json()["access_token"]
        refresh_token = login_resp.json()["refresh_token"]

        response = await client.post(
            "/auth/logout",
            json={
                "refresh_token": refresh_token,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "Logged out"

    async def test_without_auth(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/sign-up",
            json={
                "email": "noauth@test.com",
                "full_name": "NoAuth",
                "password": "pass123",
            },
        )
        login_resp = await client.post(
            "/auth/sign-in",
            data={
                "username": "noauth@test.com",
                "password": "pass123",
            },
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = await client.post(
            "/auth/logout",
            json={
                "refresh_token": refresh_token,
            },
        )
        assert response.status_code == 401
