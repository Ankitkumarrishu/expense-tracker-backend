def _login(client, username: str, password: str) -> str:
    r = client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_viewer_dashboard_ok_but_records_forbidden(client):
    token = _login(client, "viewer@test.com", "viewer12345")
    h = {"Authorization": f"Bearer {token}"}
    s = client.get("/api/dashboard/summary", headers=h)
    assert s.status_code == 200
    body = s.json()
    assert body["total_income"] == "100.00"
    assert body["recent_activity"] == []

    r = client.get("/api/records", headers=h)
    assert r.status_code == 403


def test_analyst_can_list_records_and_sees_recent(client):
    token = _login(client, "analyst@test.com", "analyst12345")
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/records", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

    s = client.get("/api/dashboard/summary", headers=h)
    assert s.status_code == 200
    assert len(s.json()["recent_activity"]) >= 1


def test_analyst_cannot_mutate_records(client):
    token = _login(client, "analyst@test.com", "analyst12345")
    h = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/api/records",
        headers=h,
        json={
            "amount": "10.00",
            "type": "expense",
            "category": "X",
            "entry_date": "2024-01-15",
        },
    )
    assert r.status_code == 403


def test_admin_crud_record(client):
    token = _login(client, "admin@test.com", "admin12345")
    h = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/api/records",
        headers=h,
        json={
            "amount": "25.50",
            "type": "expense",
            "category": "Office",
            "entry_date": "2024-02-01",
            "notes": "supplies",
        },
    )
    assert r.status_code == 201
    rid = r.json()["id"]

    u = client.patch(
        f"/api/records/{rid}",
        headers=h,
        json={"amount": "30.00"},
    )
    assert u.status_code == 200
    assert u.json()["amount"] == "30.00"

    d = client.delete(f"/api/records/{rid}", headers=h)
    assert d.status_code == 204

    g = client.get(f"/api/records/{rid}", headers=h)
    assert g.status_code == 404


def test_validation_rejects_negative_amount(client):
    token = _login(client, "admin@test.com", "admin12345")
    h = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/api/records",
        headers=h,
        json={
            "amount": "-1",
            "type": "income",
            "category": "Bad",
            "entry_date": "2024-02-01",
        },
    )
    assert r.status_code == 422


def test_admin_user_management(client):
    token = _login(client, "admin@test.com", "admin12345")
    h = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/api/users",
        headers=h,
        json={
            "email": "new@test.com",
            "password": "password12",
            "full_name": "New",
            "role": "viewer",
        },
    )
    assert r.status_code == 201

    bad = client.post(
        "/api/users",
        headers=h,
        json={
            "email": "new@test.com",
            "password": "password12",
            "role": "viewer",
        },
    )
    assert bad.status_code == 400
