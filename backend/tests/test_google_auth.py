from flask import Response

from app.extensions import db
from app.models import User


class DummyGoogle:
    def authorize_redirect(self, uri):
        return Response("redirect", status=302)

    def authorize_access_token(self):
        return {"access_token": "x"}

    def userinfo(self):
        return {"email": "g@example.com", "sub": "123"}


def test_google_login(monkeypatch, client):
    dummy = DummyGoogle()
    monkeypatch.setattr("app.routes.google_auth.oauth.google", dummy)
    res = client.get("/api/oauth/google/login")
    assert res.status_code == 302


def test_google_callback(monkeypatch, app, client):
    dummy = DummyGoogle()
    monkeypatch.setattr("app.routes.google_auth.oauth.google", dummy)

    res = client.get("/api/oauth/google/callback")
    assert res.status_code == 200
    data = res.get_json()
    assert data["user_id"]
