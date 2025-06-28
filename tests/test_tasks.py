"""test tasks api."""

from http import HTTPStatus
from typing import TYPE_CHECKING

from flask import url_for

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def test_create_task(client: "FlaskClient") -> None:
    """Test creating a task."""
    response = client.post(
        url_for("tasks"),
        json={"name": "New Task", "settings": {"priority": "high"}},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    assert response.json["result"]["items"][0]["name"] == "New Task"
    response = client.post(
        url_for("tasks"),
        json={"name": "New Task", "settings": {"priority": "high"}},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json is not None
    assert response.json["message"] == "task already exists"
    response = client.post(
        url_for("tasks"),
        json={"name": "New Task 2"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    assert response.json["result"]["items"][0]["name"] == "New Task 2"
    response = client.post(
        url_for("tasks"),
        json={},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT
    assert response.json is not None
    assert "name" in response.json["message"]


def test_get_tasks(client: "FlaskClient") -> None:
    """Test getting tasks."""
    count = 10
    for i in range(count):
        client.post(
            url_for("tasks"),
            json={"name": f"Task {i}", "settings": {"priority": "medium"}},
        )
    response = client.get(url_for("tasks"))
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    assert isinstance(response.json["result"]["items"], list)
    assert response.json["result"]["total"] == count
