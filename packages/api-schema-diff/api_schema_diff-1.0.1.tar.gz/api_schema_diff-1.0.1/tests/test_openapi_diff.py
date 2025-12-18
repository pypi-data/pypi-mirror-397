from schema_diff.openapi.diff import diff_openapi


def test_openapi_removed_path_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {"get": {"responses": {"200": {"description": "ok"}}}},
            "/orders": {"get": {"responses": {"200": {"description": "ok"}}}},
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {"get": {"responses": {"200": {"description": "ok"}}}},
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        c.path == "paths./orders" and "Path removed" in (c.message or "")
        for c in result.breaking
    )


def test_openapi_added_path_is_non_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {"/users": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {"get": {"responses": {"200": {"description": "ok"}}}},
            "/orders": {"get": {"responses": {"200": {"description": "ok"}}}},
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 0
    assert any(
        c.path == "paths./orders" and "Path added" in (c.message or "")
        for c in result.non_breaking
    )


def test_openapi_removed_operation_is_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {"responses": {"200": {"description": "ok"}}},
                "post": {"responses": {"201": {"description": "created"}}},
            }
        },
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {"responses": {"200": {"description": "ok"}}},
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 1
    assert any(
        c.path == "paths./users.post" and "Operation removed" in (c.message or "")
        for c in result.breaking
    )


def test_openapi_added_operation_is_non_breaking():
    old = {
        "openapi": "3.0.0",
        "paths": {"/users": {"get": {"responses": {"200": {"description": "ok"}}}}},
    }
    new = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {"responses": {"200": {"description": "ok"}}},
                "post": {"responses": {"201": {"description": "created"}}},
            }
        },
    }

    result = diff_openapi(old, new)
    assert result.exit_code() == 0
    assert any(
        c.path == "paths./users.post" and "Operation added" in (c.message or "")
        for c in result.non_breaking
    )
