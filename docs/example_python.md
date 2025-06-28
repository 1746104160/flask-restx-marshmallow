# Example

```python
"""Example Flask application with RESTful API using flask_restx_marshmallow."""

# ruff: noqa: PLR6301
from collections.abc import Iterable
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import TYPE_CHECKING, Self, Unpack
from uuid import UUID, uuid4

from flask.app import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy.extension import SQLAlchemy as BaseSQLAlchemy
from marshmallow.fields import Integer, Nested
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy_utils.types.json import JSONType

from flask_restx_marshmallow import Resource
from flask_restx_marshmallow.api import Api
from flask_restx_marshmallow.namespace import Namespace
from flask_restx_marshmallow.schema import Schema
from flask_restx_marshmallow.type import (
    Result,
    SchemaInitKwargs,
    Success,
    TupleResponse,
    Warn,
)
from flask_restx_marshmallow.util import class_schema, make_default_schema

try:
    from loguru import logger
except ImportError:
    from logging import getLogger

    logger = getLogger(__name__)
if TYPE_CHECKING:
    from typing import Self

    from flask_sqlalchemy.extension import _FSAModel
    from flask_sqlalchemy.query import Query
    from sqlalchemy.orm.query import Query as _Query

    class Model(_FSAModel):
        """Add original type for type annotation, which is able to use typevar."""

        query: _Query[Self] | Query

    class SQLAlchemy(BaseSQLAlchemy):
        """Add original type for type annotation, which is able to use typevar."""

        Model: type[Model]


@dataclass(kw_only=True)
class CreateTaskParameters:
    """Parameters for creating a task."""

    name: str = field(
        metadata={"metadata": {"description": "task name"}},
    )
    settings: dict | None = field(
        default=None,
        metadata={"metadata": {"description": "task settings"}},
    )


@dataclass(kw_only=True)
class UpdateTaskParameters:
    """Parameters for updating a task."""

    task_id: UUID = field(
        metadata={"metadata": {"description": "task id", "location": "path"}},
    )
    name: str | None = field(
        default=None,
        metadata={"metadata": {"description": "task name"}},
    )
    settings: dict | None = field(
        default=None,
        metadata={"metadata": {"description": "task settings"}},
    )


@dataclass(kw_only=True)
class DeleteTaskParameters:
    """Parameters for deleting a task."""

    task_id: UUID = field(
        metadata={"metadata": {"description": "task id", "location": "path"}},
    )


@dataclass(kw_only=True)
class QueryTasksParameters:
    """Parameters for querying a task."""

    name: str | None = field(
        default=None,
        metadata={"metadata": {"description": "task name"}},
    )


@dataclass(kw_only=True)
class QueryTaskParameters:
    """Parameters for querying a task."""

    task_id: "UUID | None" = field(
        default=None,
        metadata={"metadata": {"description": "task id", "location": "path"}},
    )
    name: str | None = field(
        default=None,
        metadata={"metadata": {"description": "task name"}},
    )


@dataclass(kw_only=True)
class TaskProfile:
    """Task profile schema."""

    task_id: UUID = field(
        metadata={"metadata": {"description": "task unique identifier"}},
    )
    name: str = field(metadata={"metadata": {"description": "task name"}})
    settings: dict | None = field(
        default=None,
        metadata={"metadata": {"description": "task settings"}},
    )


class TaskProfileSchema(class_schema(TaskProfile, base=Schema)):
    """Task profile schema for marshmallow serialization."""


class StandardSchema(make_default_schema(name="StandardResponse")):
    """Standard response schema."""

    def __init__(
        self,
        message: str | None = None,
        header_fields: Iterable[str] | None = None,
        **kwargs: Unpack[SchemaInitKwargs],
    ) -> None:
        """Set default message.

        Args:
            message (str | None): response message. Defaults to None.
            header_fields (Iterable[str] | None): header fields. Defaults to None.
            kwargs (Unpack[SchemaInitKwargs]): other kwargs.
        """
        super().__init__(header_fields=header_fields, **kwargs)
        if message is not None:
            self.fields["message"].dump_default = message
            self.fields["message"].metadata = dict(
                **self.fields["message"].metadata,
            )
            self.fields["message"].metadata["example"] = message


class TaskSchema(StandardSchema):
    """Query response schema for task."""

    result = Nested(
        {
            "items": Nested(
                TaskProfileSchema,
                metadata={"description": "task list"},
                many=True,
            ),
            "total": Integer(metadata={"description": "total number of tasks"}),
        },
        metadata={"description": "query result"},
    )


db = (
    SQLAlchemy()
    if TYPE_CHECKING
    else BaseSQLAlchemy(session_options={"expire_on_commit": False})
)


class Task(db.Model):
    """Task model for managing tasks in the database."""

    if TYPE_CHECKING:

        def __init__(
            self,
            *,
            task_id: UUID,
            name: str,
            settings: dict | None = None,
        ) -> None:
            """Add init annotations for type checking.

            Args:
                task_id (UUID): The unique identifier for the task.
                name (str): The name of the task.
                settings (dict, optional): The settings for the task.
                    Defaults to None.
            """

    __tablename__ = "task"
    task_id: Mapped[UUID] = mapped_column(primary_key=True, comment="task id")
    name: Mapped[str] = mapped_column(unique=True, comment="task name")
    settings: Mapped[dict | None] = mapped_column(JSONType, comment="task settings")

    @classmethod
    def create(
        cls,
        create_task_info: "CreateTaskParameters",
    ) -> TupleResponse["Self"] | TupleResponse:
        """Create a new task instance.

        Args:
            create_task_info (CreateTaskParameters): The parameters for creating.

        Returns:
            TupleResponse: A response containing the created task or an error.
                message.
        """
        try:
            task_ = cls(
                task_id=uuid4(),
                name=create_task_info.name,
                settings=create_task_info.settings,
            )
            db.session.add(task_)
            db.session.commit()
            return TupleResponse(
                Success(
                    message="create task successfully",
                    result=Result(
                        items=[task_],
                        total=1,
                    ),
                ),
            )
        except Exception:
            db.session.rollback()
            db.session.commit()
            logger.exception("task already exists: %s", create_task_info.name)
            return TupleResponse(
                Warn(message="task already exists"),
                status_code=HTTPStatus.BAD_REQUEST,
            )

    @classmethod
    def delete(
        cls,
        task_id: UUID,
    ) -> TupleResponse:
        """Delete a task instance by its ID.

        Args:
            task_id (UUID): The unique identifier for the task.

        Returns:
            TupleResponse: A response indicating the success or failure of the
                deletion.
        """
        if (query := cls.query.filter_by(task_id=task_id)).one_or_none():
            query.delete()
            return TupleResponse(Success(message="delete task successfully"))
        logger.warning("task not found: %s", task_id)
        return TupleResponse(
            Warn(message="task not found"),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    @classmethod
    def update(cls, task_update_info: "UpdateTaskParameters") -> TupleResponse:
        """Update a task instance by its ID.

        Args:
            task_update_info (UpdateTaskParameters): The parameters for updating
                the task.

        Returns:
            TupleResponse: A response indicating the success or failure of the
                update.
        """
        if task := cls.query.filter_by(
            task_id=task_update_info.task_id,
        ).one_or_none():
            if task_update_info.name is not None:
                task.name = task_update_info.name
            if task_update_info.settings is not None:
                task.settings = task_update_info.settings
            db.session.commit()
            return TupleResponse(Success(message="update task successfully"))
        logger.warning("task not found: %s", task_update_info.task_id)
        return TupleResponse(
            Warn(message="task not found"),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    @classmethod
    def query_task(cls, params: "QueryTaskParameters") -> TupleResponse["Self"]:
        """Query a task instance by its ID or name.

        Args:
            params (QueryTaskParameters): The parameters for querying the task.

        Returns:
            TupleResponse: A response containing the queried task or an error
                message.
        """
        if task := cls.query.filter_by(task_id=params.task_id).one_or_none():
            return TupleResponse(
                Success(
                    message="query task successfully",
                    result=Result(items=[task], total=1),
                ),
            )
        logger.warning("task not found: %s", params)
        return TupleResponse(
            Warn(message="task not found"),
            status_code=HTTPStatus.BAD_REQUEST,
        )

    @classmethod
    def query_tasks(cls, params: "QueryTasksParameters") -> TupleResponse["Self"]:
        """Query a task instance by its ID or name.

        Args:
            params (QueryTasksParameters): The parameters for querying the task.

        Returns:
            TupleResponse: A response containing the queried task or an error
                message.
        """
        query = cls.query
        if params.name is not None:
            query = query.filter(cls.name.ilike(params.name))
        if query.count() > 0:
            return TupleResponse(
                Success(
                    message="query task successfully",
                    result=Result(
                        items=query.all(),
                        total=query.count(),
                    ),
                ),
            )
        logger.warning("task not found: %s", params)
        return TupleResponse(
            Warn(message="task not found"),
            status_code=HTTPStatus.BAD_REQUEST,
        )


ns = Namespace(
    "example",
    description="example namespace for task management",
    path="/task",
)


@ns.route("/", endpoint="tasks")
class TasksManage(Resource):
    """tasks manage."""

    @ns.parameters(params=QueryTasksParameters, location="query")
    @ns.responses(schema=TaskSchema(message="query task success"))
    @ns.responses(message="task not found", code=HTTPStatus.BAD_REQUEST)
    def get(self, params: "QueryTasksParameters") -> "TupleResponse[Task]":
        """Query all tasks.

        Args:
            params (QueryTasksParameters): The parameters for querying tasks.

        Returns:
            TupleResponse[Task]: A response containing the queried tasks.
        """
        return Task.query_tasks(params)

    @ns.parameters(params=CreateTaskParameters, location="body")
    @ns.responses(schema=TaskSchema(message="create task successfully"))
    @ns.responses(message="task already exists", code=HTTPStatus.BAD_REQUEST)
    def post(
        self,
        params: "CreateTaskParameters",
    ) -> "TupleResponse[Task] | TupleResponse":
        """Create a new task.

        Args:
            params (CreateTaskParameters): The parameters for creating a task.

        Returns:
            TupleResponse[Task]: A response containing the created task.
        """
        return Task.create(params)


@ns.route("/<task_id>", endpoint="task")
class TaskManage(Resource):
    """task manage."""

    @ns.parameters(params=QueryTaskParameters, location="query")
    @ns.responses(schema=TaskSchema(message="query task success"))
    @ns.responses(message="task not found", code=HTTPStatus.BAD_REQUEST)
    def get(self, params: "QueryTaskParameters", **_) -> "TupleResponse[Task]":  # noqa: ANN003
        """Query a task by its ID or name.

        Args:
            params (QueryTaskParameters): The parameters for querying the task.

        Returns:
            TupleResponse[Task]: A response containing the queried task.
        """
        return Task.query_task(params)

    @ns.parameters(params=DeleteTaskParameters, location="path")
    @ns.responses(message="delete task successfully")
    @ns.responses(message="task not found", code=HTTPStatus.BAD_REQUEST)
    def delete(self, params: "DeleteTaskParameters", **_) -> "TupleResponse":  # noqa: ANN003
        """Delete a task by its ID.

        Args:
            params (DeleteTaskParameters): The parameters for deleting the task.

        Returns:
            TupleResponse: A response indicating the success or failure of the
                deletion.
        """
        return Task.delete(params.task_id)

    @ns.parameters(params=UpdateTaskParameters, location="body")
    @ns.responses(message="update task successfully")
    @ns.responses(message="task not found", code=HTTPStatus.BAD_REQUEST)
    def patch(self, params: "UpdateTaskParameters", **_) -> "TupleResponse":  # noqa: ANN003
        """Update a task by its ID.

        Args:
            params (UpdateTaskParameters): The parameters for updating the task.

        Returns:
            TupleResponse: A response indicating the success or failure of the
                update.
        """
        return Task.update(params)


api = Api(
    version="0.2.0",
    title="example API",
    description="api interface for example app",
)
api.add_namespace(ns)
app = Flask(__name__, subdomain_matching=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
app.test_client_class = FlaskClient
api.init_app(app)
db.init_app(app)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

```