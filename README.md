# Flask-RESTX-marshmallow

[![PyPI version](https://badge.fury.io/py/flask-restx-marshmallow.svg)](https://badge.fury.io/py/flask-restx-marshmallow)
[![Python version](https://img.shields.io/pypi/pyversions/flask-restx-marshmallow.svg)](https://pypi.org/project/flask-restx-marshmallow/)
[![License](https://img.shields.io/pypi/l/flask-restx-marshmallow.svg)](https://github.com/1746104160/flask-restx-marshmallow/blob/main/LICENSE)

Flask-RESTX-marshmallow is a powerful extension that seamlessly combines [Flask](https://flask.palletsprojects.com/en/latest/), [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/), and [Marshmallow](https://marshmallow.readthedocs.io/en/stable/) to provide a robust foundation for building RESTful APIs with automatic documentation and data validation.

## ✨ Features

- 🚀 **Seamless Integration**: Combines Flask-RESTX's API documentation with Marshmallow's powerful serialization
- 📋 **Automatic Documentation**: Generate interactive Swagger/OpenAPI documentation automatically
- 🔍 **Data Validation**: Built-in request/response validation using Marshmallow schemas
- 🎯 **Type Safety**: Full type hint support for better development experience
- 🔧 **Easy Configuration**: Minimal setup required to get started
- 📦 **SQLAlchemy Integration**: Works perfectly with Flask-SQLAlchemy

## 🔧 Requirements

- Python 3.12+
- Flask 3.1+
- Flask-RESTX 1.3+
- Marshmallow 4.0+

## 📦 Installation

Install the extension with pip:

```bash
pip install flask-restx-marshmallow
```

or with poetry:

```bash
poetry add flask-restx-marshmallow
```

or with uv

```bash
uv add flask-restx-marshmallow
```

## 🚀 Quick Start

### Complete Example

For a comprehensive example with SQLAlchemy integration, see `app.py`. This example demonstrates:

- RESTful API endpoints with full CRUD operations
- Automatic request/response validation
- Interactive Swagger documentation
- Database integration with Flask-SQLAlchemy
- Error handling and status codes

The example application provides these endpoints:

| Endpoint         | Method | Description                                    |
| ---------------- | ------ | ---------------------------------------------- |
| `/tasks/`        | GET    | Query all tasks with optional filtering        |
| `/tasks/`        | POST   | Create a new task                              |
| `/tasks/<id>`    | GET    | Retrieve a specific task by ID                 |
| `/tasks/<id>`    | PATCH  | Update a task partially                        |
| `/tasks/<id>`    | DELETE | Delete a task by ID                            |

## 🏃‍♂️ Running the Example

1. Clone the repository:

    ```
    git clone https://github.com/1746104160/flask-restx-marshmallow.git && cd flask-restx-marshmallow
    ```

2. Install dependencies:

    ```
    poetry install --with dev
    ```
    or
    ```
    uv sync --dev
    ```

3. Run the example application:

    ```
    python app.py
    ```
    or
    ```
    flask run
    ```

4. Visit `http://localhost:5000` to explore the interactive API documentation.

## 📚 Documentation

Visit the interactive API documentation when running your application to explore all available endpoints and schemas. The documentation is automatically generated from your code and provides:

- **Interactive API testing**: Try out endpoints directly from the browser
- **Schema visualization**: See request/response models with examples
- **Parameter documentation**: Understand required and optional parameters
- **Error responses**: Learn about possible error scenarios

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- [GitHub Repository](https://github.com/1746104160/flask-restx-marshmallow)
- [PyPI Package](https://pypi.org/project/flask-restx-marshmallow/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-RESTX Documentation](https://flask-restx.readthedocs.io/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!
