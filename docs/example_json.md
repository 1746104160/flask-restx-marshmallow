# Example

```json
{
  "openapi": "3.1.1",
  "info": {
    "title": "example API",
    "version": "0.2.0",
    "description": "api interface for example app",
    "contact": {}
  },
  "servers": [
    {
      "url": "{scheme}://{host}{basepath}",
      "description": "default server",
      "variables": {
        "scheme": {
          "enum": ["http", "https"],
          "default": "http",
          "description": "http or https"
        },
        "host": {
          "enum": ["127.0.0.1:5000"],
          "default": "127.0.0.1:5000",
          "description": "host"
        },
        "basepath": { "default": "/", "description": "basepath" }
      }
    }
  ],
  "paths": {
    "/task/": {
      "get": {
        "tags": ["example"],
        "operationId": "example.TasksManage.get.task",
        "responses": {
          "default": {
            "description": "Query response schema for task.",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/TaskSchemaBody" },
                "example": {
                  "code": 0,
                  "message": "query task success",
                  "result": null
                }
              }
            }
          },
          "400": {
            "description": "Bad Request",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TasksmanageGetSchemaBody"
                },
                "examples": {
                  "TasksmanageGetSchema": {
                    "summary": "Query all tasks.",
                    "description": "Query all tasks.",
                    "value": { "code": 0, "message": "task not found" }
                  },
                  "BadRequestSchema": {
                    "summary": "Bad request.",
                    "description": "Bad request.",
                    "value": {
                      "code": -1,
                      "message": "Bad request syntax or unsupported method"
                    }
                  }
                }
              }
            }
          },
          "200": {
            "description": "Query response schema for task.",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/TaskSchemaBody" },
                "example": {
                  "code": 0,
                  "message": "query task success",
                  "result": null
                }
              }
            }
          },
          "422": {
            "description": "Unprocessable Entity Schema.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UnprocessableEntitySchemaBody"
                },
                "example": {
                  "code": -1,
                  "message": { "field": ["Unprocessable Entity"] }
                }
              }
            }
          },
          "500": {
            "description": "Internal Server Error Schema.",
            "content": {
              "text/plain": {
                "schema": { "type": "string" },
                "example": "Internal Server Error"
              }
            }
          }
        },
        "deprecated": false,
        "summary": "Query all tasks.",
        "parameters": [
          {
            "in": "query",
            "name": "name",
            "description": "task name",
            "schema": {
              "type": ["string", "null"],
              "default": null,
              "writeOnly": true
            },
            "required": false
          }
        ]
      },
      "post": {
        "tags": ["example"],
        "operationId": "example.TasksManage.post.task",
        "responses": {
          "default": {
            "description": "Query response schema for task.",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/TaskSchemaBody" },
                "example": {
                  "code": 0,
                  "message": "create task successfully",
                  "result": null
                }
              }
            }
          },
          "400": {
            "description": "Bad Request",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TasksmanagePostSchemaBody"
                },
                "examples": {
                  "TasksmanagePostSchema": {
                    "summary": "Create a new task.",
                    "description": "Create a new task.",
                    "value": { "code": 0, "message": "task already exists" }
                  },
                  "BadRequestSchema": {
                    "summary": "Bad request.",
                    "description": "Bad request.",
                    "value": {
                      "code": -1,
                      "message": "Bad request syntax or unsupported method"
                    }
                  }
                }
              }
            }
          },
          "200": {
            "description": "Query response schema for task.",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/TaskSchemaBody" },
                "example": {
                  "code": 0,
                  "message": "create task successfully",
                  "result": null
                }
              }
            }
          },
          "422": {
            "description": "Unprocessable Entity Schema.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UnprocessableEntitySchemaBody"
                },
                "example": {
                  "code": -1,
                  "message": { "field": ["Unprocessable Entity"] }
                }
              }
            }
          },
          "500": {
            "description": "Internal Server Error Schema.",
            "content": {
              "text/plain": {
                "schema": { "type": "string" },
                "example": "Internal Server Error"
              }
            }
          }
        },
        "deprecated": false,
        "summary": "Create a new task.",
        "requestBody": {
          "description": "Request parameters",
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CreateTaskParametersBody"
              },
              "example": { "name": null, "settings": null }
            }
          },
          "required": true
        }
      },
      "summary": "tasks manage."
    },
    "/task/{task_id}": {
      "get": {
        "tags": ["example"],
        "operationId": "example.TaskManage.get.task_",
        "responses": {
          "default": {
            "description": "Query response schema for task.",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/TaskSchemaBody" },
                "example": {
                  "code": 0,
                  "message": "query task success",
                  "result": null
                }
              }
            }
          },
          "400": {
            "description": "Bad Request",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskmanageGetSchemaBody"
                },
                "examples": {
                  "TaskmanageGetSchema": {
                    "summary": "Query a task by its ID or name.",
                    "description": "Query a task by its ID or name.",
                    "value": { "code": 0, "message": "task not found" }
                  },
                  "BadRequestSchema": {
                    "summary": "Bad request.",
                    "description": "Bad request.",
                    "value": {
                      "code": -1,
                      "message": "Bad request syntax or unsupported method"
                    }
                  }
                }
              }
            }
          },
          "200": {
            "description": "Query response schema for task.",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/TaskSchemaBody" },
                "example": {
                  "code": 0,
                  "message": "query task success",
                  "result": null
                }
              }
            }
          },
          "422": {
            "description": "Unprocessable Entity Schema.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UnprocessableEntitySchemaBody"
                },
                "example": {
                  "code": -1,
                  "message": { "field": ["Unprocessable Entity"] }
                }
              }
            }
          },
          "500": {
            "description": "Internal Server Error Schema.",
            "content": {
              "text/plain": {
                "schema": { "type": "string" },
                "example": "Internal Server Error"
              }
            }
          }
        },
        "deprecated": false,
        "summary": "Query a task by its ID or name.",
        "parameters": [
          {
            "in": "path",
            "name": "task_id",
            "description": "task id",
            "schema": {
              "type": ["string", "null"],
              "format": "uuid",
              "default": null,
              "writeOnly": true
            },
            "required": true
          },
          {
            "in": "query",
            "name": "name",
            "description": "task name",
            "schema": {
              "type": ["string", "null"],
              "default": null,
              "writeOnly": true
            },
            "required": false
          }
        ]
      },
      "patch": {
        "tags": ["example"],
        "operationId": "example.TaskManage.patch.task_",
        "responses": {
          "default": {
            "description": "OK",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskmanagePatchSchemaBody"
                },
                "example": { "code": 0, "message": "update task successfully" }
              }
            }
          },
          "400": {
            "description": "Bad Request",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskmanagePatchSchemaBody"
                },
                "examples": {
                  "TaskmanagePatchSchema": {
                    "summary": "Update a task by its ID.",
                    "description": "Update a task by its ID.",
                    "value": { "code": 0, "message": "task not found" }
                  },
                  "BadRequestSchema": {
                    "summary": "Bad request.",
                    "description": "Bad request.",
                    "value": {
                      "code": -1,
                      "message": "Bad request syntax or unsupported method"
                    }
                  }
                }
              }
            }
          },
          "200": {
            "description": "OK",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskmanagePatchSchemaBody"
                },
                "example": { "code": 0, "message": "update task successfully" }
              }
            }
          },
          "422": {
            "description": "Unprocessable Entity Schema.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UnprocessableEntitySchemaBody"
                },
                "example": {
                  "code": -1,
                  "message": { "field": ["Unprocessable Entity"] }
                }
              }
            }
          },
          "500": {
            "description": "Internal Server Error Schema.",
            "content": {
              "text/plain": {
                "schema": { "type": "string" },
                "example": "Internal Server Error"
              }
            }
          }
        },
        "deprecated": false,
        "summary": "Update a task by its ID.",
        "parameters": [
          {
            "in": "path",
            "name": "task_id",
            "description": "task id",
            "schema": { "type": "string", "format": "uuid", "writeOnly": true },
            "required": true
          }
        ],
        "requestBody": {
          "description": "Request parameters",
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/UpdateTaskParametersBody"
              },
              "example": { "name": null, "settings": null }
            }
          },
          "required": false
        }
      },
      "delete": {
        "tags": ["example"],
        "operationId": "example.TaskManage.delete.task_",
        "responses": {
          "default": {
            "description": "OK",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskmanageDeleteSchemaBody"
                },
                "example": { "code": 0, "message": "delete task successfully" }
              }
            }
          },
          "400": {
            "description": "Bad Request",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskmanageDeleteSchemaBody"
                },
                "examples": {
                  "TaskmanageDeleteSchema": {
                    "summary": "Delete a task by its ID.",
                    "description": "Delete a task by its ID.",
                    "value": { "code": 0, "message": "task not found" }
                  },
                  "BadRequestSchema": {
                    "summary": "Bad request.",
                    "description": "Bad request.",
                    "value": {
                      "code": -1,
                      "message": "Bad request syntax or unsupported method"
                    }
                  }
                }
              }
            }
          },
          "200": {
            "description": "OK",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/TaskmanageDeleteSchemaBody"
                },
                "example": { "code": 0, "message": "delete task successfully" }
              }
            }
          },
          "422": {
            "description": "Unprocessable Entity Schema.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UnprocessableEntitySchemaBody"
                },
                "example": {
                  "code": -1,
                  "message": { "field": ["Unprocessable Entity"] }
                }
              }
            }
          },
          "500": {
            "description": "Internal Server Error Schema.",
            "content": {
              "text/plain": {
                "schema": { "type": "string" },
                "example": "Internal Server Error"
              }
            }
          }
        },
        "deprecated": false,
        "summary": "Delete a task by its ID.",
        "parameters": [
          {
            "in": "path",
            "name": "task_id",
            "description": "task id",
            "schema": { "type": "string", "format": "uuid", "writeOnly": true },
            "required": true
          }
        ]
      },
      "summary": "task manage."
    }
  },
  "components": {
    "schemas": {
      "BadRequestSchema": {
        "type": "object",
        "properties": {
          "code": {
            "default": -1,
            "readOnly": true,
            "description": "response code",
            "example": -1,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "Bad request syntax or unsupported method",
            "readOnly": true,
            "description": "response message",
            "example": "Bad request syntax or unsupported method"
          }
        }
      },
      "UnprocessableEntitySchema": {
        "type": "object",
        "properties": {
          "code": {
            "default": -1,
            "readOnly": true,
            "description": "response code",
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": "object",
            "default": { "field": ["Unprocessable Entity"] },
            "readOnly": true,
            "description": "message",
            "additionalProperties": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "required": ["code", "message"]
      },
      "HTTPError500Schema": {
        "type": "object",
        "properties": {
          "message": {
            "type": "string",
            "readOnly": true,
            "description": "message",
            "example": "Internal Server Error"
          }
        }
      },
      "TasksmanageGetSchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": 0,
            "readOnly": true,
            "description": "response code",
            "example": 0,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "task not found",
            "readOnly": true,
            "description": "response message",
            "example": "task not found"
          }
        }
      },
      "BadRequestSchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": -1,
            "readOnly": true,
            "description": "response code",
            "example": -1,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "Bad request syntax or unsupported method",
            "readOnly": true,
            "description": "response message",
            "example": "Bad request syntax or unsupported method"
          }
        }
      },
      "TaskProfileSchema": {
        "type": "object",
        "properties": {
          "task_id": {
            "type": "string",
            "format": "uuid",
            "readOnly": true,
            "description": "task unique identifier"
          },
          "name": {
            "type": "string",
            "readOnly": true,
            "description": "task name"
          },
          "settings": {
            "type": ["object", "null"],
            "default": null,
            "readOnly": true,
            "description": "task settings",
            "additionalProperties": {}
          }
        },
        "required": ["name", "task_id"]
      },
      "GeneratedSchema": {
        "type": "object",
        "properties": {
          "items": {
            "description": "task list",
            "type": "array",
            "items": { "$ref": "#/components/schemas/TaskProfileSchema" }
          },
          "total": { "type": "integer", "description": "total number of tasks" }
        }
      },
      "TaskSchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": 0,
            "readOnly": true,
            "description": "response code",
            "example": 0,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "Request success",
            "readOnly": true,
            "description": "response message",
            "example": "query task success"
          },
          "result": {
            "readOnly": true,
            "description": "query result",
            "$ref": "#/components/schemas/GeneratedSchema"
          }
        }
      },
      "UnprocessableEntitySchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": -1,
            "readOnly": true,
            "description": "response code",
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": "object",
            "default": { "field": ["Unprocessable Entity"] },
            "readOnly": true,
            "description": "message",
            "additionalProperties": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },
        "required": ["code", "message"]
      },
      "CreateTaskParametersBody": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "writeOnly": true,
            "description": "task name"
          },
          "settings": {
            "type": ["object", "null"],
            "default": null,
            "writeOnly": true,
            "description": "task settings",
            "additionalProperties": {}
          }
        },
        "required": ["name"]
      },
      "TasksmanagePostSchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": 0,
            "readOnly": true,
            "description": "response code",
            "example": 0,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "task already exists",
            "readOnly": true,
            "description": "response message",
            "example": "task already exists"
          }
        }
      },
      "TaskmanageGetSchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": 0,
            "readOnly": true,
            "description": "response code",
            "example": 0,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "task not found",
            "readOnly": true,
            "description": "response message",
            "example": "task not found"
          }
        }
      },
      "UpdateTaskParametersBody": {
        "type": "object",
        "properties": {
          "name": {
            "type": ["string", "null"],
            "default": null,
            "writeOnly": true,
            "description": "task name"
          },
          "settings": {
            "type": ["object", "null"],
            "default": null,
            "writeOnly": true,
            "description": "task settings",
            "additionalProperties": {}
          }
        }
      },
      "TaskmanagePatchSchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": 0,
            "readOnly": true,
            "description": "response code",
            "example": 0,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "task not found",
            "readOnly": true,
            "description": "response message",
            "example": "task not found"
          }
        }
      },
      "TaskmanageDeleteSchemaBody": {
        "type": "object",
        "properties": {
          "code": {
            "default": 0,
            "readOnly": true,
            "description": "response code",
            "example": 0,
            "type": "integer",
            "enum": [0, -1, 1]
          },
          "message": {
            "type": ["string", "null"],
            "default": "task not found",
            "readOnly": true,
            "description": "response message",
            "example": "task not found"
          }
        }
      }
    }
  },
  "tags": [
    {
      "name": "example",
      "description": "example namespace for task management"
    }
  ]
}
```
