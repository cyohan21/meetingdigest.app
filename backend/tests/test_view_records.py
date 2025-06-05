from app.models import User, Record
from app.extensions import db
from datetime import datetime, timezone

def test_get_all_records_empty(client, auth_headers):
    res = client.get("/records/view", headers=auth_headers)

    print("\n=== DEBUG ===")
    print("Status code:", res.status_code)
    print("Response JSON:", res.get_json())
    print("Headers sent:", auth_headers)
    print("=== END ===\n")

    assert res.status_code == 200
    assert res.get_json() == {"msg": "No records found."}

def test_get_all_records_with_data(app, client, auth_headers):
    with app.app_context():
        user = User.query.first()
        record = Record(
            user_id=user.id,
            filename="test.mp3",
            summary="Test summary",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(record)
        db.session.commit()

    res = client.get("/records/view", headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["filename"] == "test.mp3"

def test_view_specific_record(client, auth_headers, app):
    with app.app_context():
        user = User.query.first()
        record = Record(
            user_id=user.id,
            filename="specific.mp3",
            transcript="Hello world",
            summary="Summary",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(record)
        db.session.commit()
        record_id = record.id

    res = client.get(f"/records/view/{record_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["filename"] == "specific.mp3"

def test_delete_record(client, auth_headers, app):
    with app.app_context():
        user = User.query.first()
        record = Record(
            user_id=user.id,
            filename="delete.mp3",
            transcript="to be deleted",
            summary="bye",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(record)
        db.session.commit()
        record_id = record.id

    res = client.delete(f"/records/view/{record_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json() == {"msg": "Record deleted."}