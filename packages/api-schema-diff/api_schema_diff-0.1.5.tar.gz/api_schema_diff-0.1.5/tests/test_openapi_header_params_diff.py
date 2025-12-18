from __future__ import annotations

from schema_diff.openapi.diff import diff_openapi


def test_removed_header_param_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "X-API-Version",
                            "in": "header",
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
        "paths": {"/users": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        "parameters.header.X-API-Version" in c.path
        and "removed" in (c.message or "").lower()
        for c in result.breaking
    )


def test_added_optional_header_param_is_non_breaking():
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
                            "name": "X-API-Version",
                            "in": "header",
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
        "parameters.header.X-API-Version" in c.path
        and "optional parameter added" in (c.message or "").lower()
        for c in result.non_breaking
    )


def test_added_required_header_param_is_breaking():
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
                            "name": "Authorization",
                            "in": "header",
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
        "parameters.header.Authorization" in c.path
        and "required parameter added" in (c.message or "").lower()
        for c in result.breaking
    )


def test_header_param_schema_type_change_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "parameters": [
                        {
                            "name": "X-API-Version",
                            "in": "header",
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
                            "name": "X-API-Version",
                            "in": "header",
                            "required": False,
                            "schema": {"type": "integer"},
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
        "parameters.header.X-API-Version.schema" in c.path
        and "type changed" in (c.message or "").lower()
        for c in result.breaking
    )
