from httpx import AsyncClient


async def _sign_up_and_login(client: AsyncClient, email: str, password: str = "pass123") -> str:
    await client.post(
        "/auth/sign-up",
        json={
            "email": email,
            "full_name": "Test User",
            "password": password,
        },
    )
    login_resp = await client.post(
        "/auth/sign-in",
        data={
            "username": email,
            "password": password,
        },
    )
    return login_resp.json()["access_token"]


class TestGetMe:
    async def test_success(self, client: AsyncClient) -> None:
        token = await _sign_up_and_login(client, "me@test.com")
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@test.com"
        assert data["full_name"] == "Test User"
        assert "id" in data

    async def test_unauthorized(self, client: AsyncClient) -> None:
        response = await client.get("/users/me")
        assert response.status_code == 401


class TestGetMyAccounts:
    async def test_empty(self, client: AsyncClient) -> None:
        token = await _sign_up_and_login(client, "accounts_empty@test.com")
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/users/me/accounts", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_unauthorized(self, client: AsyncClient) -> None:
        response = await client.get("/users/me/accounts")
        assert response.status_code == 401


class TestGetMyPayments:
    async def test_empty(self, client: AsyncClient) -> None:
        token = await _sign_up_and_login(client, "payments_empty@test.com")
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/users/me/payments", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_unauthorized(self, client: AsyncClient) -> None:
        response = await client.get("/users/me/payments")
        assert response.status_code == 401
