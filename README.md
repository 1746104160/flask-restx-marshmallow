<!--
 * @Description: README for flask_restx_marshmallow
 * @version: 0.1.0
 * @Author: 1746104160
 * @Date: 2023-06-02 13:05:58
 * @LastEditors: 1746104160 shaojiahong2001@outlook.com
 * @LastEditTime: 2023-06-16 18:04:55
 * @FilePath: /flask_restx_marshmallow/README.md
-->
# Flask-RESTX-marshmallow

Flask-RESTX-marshmallow is an extension for [Flask](https://flask.palletsprojects.com/en/latest/) and [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/), which is a successful practice combining flask_restx with marshmallow.

## Compatibility

Flask-RESTX-marshmallow requires Python 3.10+.

## Installation

Install the extension with pip:

```bash
pip install flask-restx-marshmallow
```

or with poetry:

```bash
poetry add flask-restx-marshmallow
```

## Quickstart

With Flask-RESTX-marshmallow, you only import the api instance to route and document your endpoints.

```python
import uuid

import sqlalchemy as sa
from flask import Flask
from marshmallow import fields, post_load

from flask_restx_marshmallow import (
    Api,
    JSONParameters,
    QueryParameters,
    Resource,
    SQLAlchemy,
    StandardSchema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
api = Api(
    app,
    version="0.1.0",
    title="example API",
    description="api interface for example app",
)
db = SQLAlchemy(app)
ns = api.namespace("example", description="example operations")


class Task(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    task = db.Column(db.String(80))

    def __init__(self, id, task):
        self.id = id.hex
        self.task = task

    def __repr__(self):
        return "<Task %r>" % self.task


class QueryTaskParameters(QueryParameters):
    id = fields.UUID(metadata={"description": "The task unique identifier"})

    @post_load
    def process(self, data, **_kwargs):
        if "id" in data:
            return {"data": Task.query.filter_by(id=data["id"].hex).first()}
        return {"code": 1, "message": "id is required", "success": False}


class CreateTaskParameters(JSONParameters):
    task = fields.String(
        required=True, metadata={"description": "The task details"}
    )

    @post_load
    def process(self, data, **_kwargs):
        try:
            task = Task(id=uuid.uuid4(), task=data["task"])
            db.session.add(task)
        except sa.exc.IntegrityError as e:
            db.session.rollback()
            return {"code": 1, "message": str(e), "success": False}
        else:
            db.session.commit()
            return {
                "message": f"create task success with id {uuid.UUID(task.id)}"
            }


class TaskSchema(StandardSchema):
    data = fields.Nested(
        {
            "id": fields.UUID(
                metadata={"description": "The task unique identifier"},
            ),
            "task": fields.String(metadata={"description": "The task details"}),
        }
    )


@ns.route("/")
class TaskManage(Resource):
    """task manage"""

    @ns.parameters(params=QueryTaskParameters(), location="query")
    @ns.response(
        code=200,
        description="query task by id",
        model=TaskSchema(message="query task success"),
    )
    def get(self, task):
        """query task by id"""
        return task

    @ns.parameters(params=CreateTaskParameters(), location="body")
    @ns.response(
        code=200,
        description="create a new task",
        model=None,
        name="CreateSchema",
        message="create successfully",
    )
    def post(self, res):
        """create a new task"""
        return res


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    api.register_doc(app)
    app.run(debug=True)
```
