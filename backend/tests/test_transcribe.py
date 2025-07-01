from io import BytesIO

from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User
import tempfile



def test_transcribe(monkeypatch, app, client):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr("app.routes.record.UPLOAD_FOLDER", tmpdir)

    with app.app_context():
        user = User(email="t@example.com", username="tuser", is_email_confirmed=True)
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id))

    def fake_transcribe(path):
        return "hello"

    def fake_summarize(text):
        return "summary"

    monkeypatch.setattr("app.routes.record.transcribe_audio", fake_transcribe)
    monkeypatch.setattr("app.routes.record.summarize_transcript", fake_summarize)

    data = {"file": (BytesIO(b"abc"), "test.wav")}
    res = client.post("/transcribe", headers={"Authorization": f"Bearer {token}"}, data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    json = res.get_json()
    assert json["summary"] == "summary"