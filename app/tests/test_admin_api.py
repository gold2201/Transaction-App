import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.factories import create_account, create_user


async def _get_admin_token(client: AsyncClient, db_session: AsyncSession) -> str:
    await create_user(db_session, email="admin@test.com", password="admin123", is_admin=True)
    resp = await client.post("/auth/sign-in", data={"username": "admin@test.com", "password": "admin123"})
    return resp.json()["access_token"]


class TestListUsers:
    async def test_empty_list(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "admin@test.com"

    async def test_with_users(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        await create_user(db_session, email="user1@test.com", password="pass1")
        await create_user(db_session, email="user2@test.com", password="pass2")
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        emails = {u["email"] for u in data}
        assert "user1@test.com" in emails
        assert "user2@test.com" in emails

    async def test_forbidden_for_non_admin(self, client: AsyncClient) -> None:
        await client.post("/auth/sign-up", json={"email": "user@test.com", "full_name": "User", "password": "pass123"})
        resp = await client.post("/auth/sign-in", data={"username": "user@test.com", "password": "pass123"})
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/admin/users", headers=headers)
        assert response.status_code == 403


class TestCreateUser:
    async def test_success(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/admin/users",
            json={
                "email": "created@test.com",
                "full_name": "Created User",
                "password": "pass123",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "created@test.com"
        assert data["full_name"] == "Created User"
        assert data["is_admin"] is False

    async def test_duplicate_email(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        await client.post(
            "/admin/users",
            json={
                "email": "dup@test.com",
                "full_name": "First",
                "password": "pass123",
            },
            headers=headers,
        )
        response = await client.post(
            "/admin/users",
            json={
                "email": "dup@test.com",
                "full_name": "Second",
                "password": "pass123",
            },
            headers=headers,
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_forbidden(self, client: AsyncClient) -> None:
        await client.post("/auth/sign-up", json={"email": "user@test.com", "full_name": "User", "password": "pass123"})
        resp = await client.post("/auth/sign-in", data={"username": "user@test.com", "password": "pass123"})
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/admin/users",
            json={
                "email": "created@test.com",
                "full_name": "Created",
                "password": "pass123",
            },
            headers=headers,
        )
        assert response.status_code == 403


class TestUpdateUser:
    async def test_success(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        user = await create_user(db_session, email="update@test.com", full_name="Old Name", password="oldpass")
        response = await client.put(
            f"/admin/users/{user.id}",
            json={
                "full_name": "New Name",
                "password": "newpass",
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "New Name"

    async def test_not_found(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = str(uuid.uuid4())
        response = await client.put(f"/admin/users/{fake_id}", json={"full_name": "Doesn't matter"}, headers=headers)
        assert response.status_code == 404

    async def test_forbidden(self, client: AsyncClient) -> None:
        await client.post("/auth/sign-up", json={"email": "user@test.com", "full_name": "User", "password": "pass123"})
        resp = await client.post("/auth/sign-in", data={"username": "user@test.com", "password": "pass123"})
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.put(f"/admin/users/{uuid.uuid4()}", json={"full_name": "New"}, headers=headers)
        assert response.status_code == 403


class TestDeleteUser:
    async def test_success(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        user = await create_user(db_session, email="delete@test.com", password="pass123")
        response = await client.delete(f"/admin/users/{user.id}", headers=headers)
        assert response.status_code == 204
        list_resp = await client.get("/admin/users", headers=headers)
        assert len(list_resp.json()) == 1

    async def test_not_found(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = str(uuid.uuid4())
        response = await client.delete(f"/admin/users/{fake_id}", headers=headers)
        assert response.status_code == 404

    async def test_forbidden(self, client: AsyncClient) -> None:
        await client.post("/auth/sign-up", json={"email": "user@test.com", "full_name": "User", "password": "pass123"})
        resp = await client.post("/auth/sign-in", data={"username": "user@test.com", "password": "pass123"})
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.delete(f"/admin/users/{uuid.uuid4()}", headers=headers)
        assert response.status_code == 403


class TestGetUserAccounts:
    async def test_empty(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        user = await create_user(db_session, email="accounts_user@test.com", password="pass123")
        response = await client.get(f"/admin/users/{user.id}/accounts", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_with_accounts(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        user = await create_user(db_session, email="with_acc@test.com", password="pass123")
        await create_account(db_session, user_id=user.id, balance=100.0)
        await create_account(db_session, user_id=user.id, balance=200.0)
        response = await client.get(f"/admin/users/{user.id}/accounts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_user_not_found(self, client: AsyncClient, db_session: AsyncSession) -> None:
        token = await _get_admin_token(client, db_session)
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/admin/users/{fake_id}/accounts", headers=headers)
        assert response.status_code == 404

    async def test_forbidden(self, client: AsyncClient) -> None:
        await client.post("/auth/sign-up", json={"email": "user@test.com", "full_name": "User", "password": "pass123"})
        resp = await client.post("/auth/sign-in", data={"username": "user@test.com", "password": "pass123"})
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"/admin/users/{uuid.uuid4()}/accounts", headers=headers)
        assert response.status_code == 403
