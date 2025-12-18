from schema_diff.openapi.diff import diff_openapi


def test_removed_query_param_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "parameters.query.q" in c.path and "removed" in (c.message or "").lower()
        for c in result.breaking
    )


def test_added_optional_query_param_is_non_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {"/users": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 0
    assert any(
        "parameters.query.q" in c.path
        and "optional parameter added" in (c.message or "").lower()
        for c in result.non_breaking
    )


def test_added_required_query_param_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {"/users": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "parameters.query.q" in c.path
        and "required parameter added" in (c.message or "").lower()
        for c in result.breaking
    )


def test_param_optional_to_required_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "parameters.query.q.required" in c.path
        and "became required" in (c.message or "").lower()
        for c in result.breaking
    )


def test_param_schema_type_change_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "parameters.query.limit.schema" in c.path
        and "type changed" in (c.message or "").lower()
        for c in result.breaking
    )


def test_path_item_parameters_apply_to_operations():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users/{id}": {
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "get": {"responses": {"200": {"description": "ok"}}},
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users/{id}": {
                # removed path param at path-item level
                "get": {"responses": {"200": {"description": "ok"}}},
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "parameters.path.id" in c.path and "removed" in (c.message or "").lower()
        for c in result.breaking
    )
