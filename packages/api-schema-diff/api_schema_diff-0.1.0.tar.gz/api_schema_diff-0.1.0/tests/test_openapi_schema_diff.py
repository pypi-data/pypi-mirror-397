from __future__ import annotations

from schema_diff.openapi.diff import diff_openapi


def test_request_schema_removed_property_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "age": {"type": "integer"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "age": {"type": "integer"}
                                    },  # removed email
                                }
                            }
                        },
                    },
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "requestBody.schema.properties.email" in c.path
        and "removed" in (c.message or "").lower()
        for c in result.breaking
    )


def test_request_optional_to_required_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "required": False,
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "requestBody.required" in c.path and "required" in (c.message or "").lower()
        for c in result.breaking
    )


def test_response_schema_type_change_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {"schema": {"type": "string"}}
                            },
                        }
                    }
                }
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"id": {"type": "integer"}},
                                    }
                                }
                            },
                        }
                    }
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "responses.200.schema" in c.path and "type changed" in (c.message or "").lower()
        for c in result.breaking
    )


def test_ref_resolution_in_components_schemas():
    old = {
        "openapi": "3.0.0",
        "components": {
            "schemas": {
                "User": {"type": "object", "properties": {"email": {"type": "string"}}}
            }
        },
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            },
                        }
                    }
                }
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "components": {
            "schemas": {"User": {"type": "object", "properties": {}}}
        },  # email removed
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            },
                        }
                    }
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "responses.200.schema.properties.email" in c.path for c in result.breaking
    )
