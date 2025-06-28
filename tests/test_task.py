"""test tasks api."""

from http import HTTPStatus
from typing import TYPE_CHECKING

from flask import url_for

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def test_get_task_by_id(client: "FlaskClient") -> None:
    """Test getting tasks."""
    response = client.post(
        url_for("tasks"),
        json={"name": "Task", "settings": {"priority": "medium"}},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    task_id = response.json["result"]["items"][0]["task_id"]
    response = client.get(url_for("task", task_id=task_id))
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    assert isinstance(response.json["result"]["items"], list)
    assert response.json["result"]["total"] == 1


def test_update_task_by_id(client: "FlaskClient") -> None:
    """Test getting tasks."""
    response = client.post(
        url_for("tasks"),
        json={"name": "Task", "settings": {"priority": "medium"}},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    task_id = response.json["result"]["items"][0]["task_id"]
    response = client.patch(
        url_for("task", task_id=task_id),
        json={"name": "Updated Task", "settings": {"priority": "low"}},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    assert response.json["message"] == "update task successfully"


def test_delete_task_by_id(client: "FlaskClient") -> None:
    """Test deleting a task."""
    response = client.post(
        url_for("tasks"),
        json={"name": "Task to Delete", "settings": {"priority": "medium"}},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    task_id = response.json["result"]["items"][0]["task_id"]
    response = client.delete(url_for("task", task_id=task_id))
    assert response.status_code == HTTPStatus.OK
    assert response.json is not None
    assert response.json["message"] == "delete task successfully"
