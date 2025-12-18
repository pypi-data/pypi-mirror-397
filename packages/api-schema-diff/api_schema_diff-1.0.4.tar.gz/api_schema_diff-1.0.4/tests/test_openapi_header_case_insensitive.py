from schema_diff.openapi.diff import diff_openapi


def test_header_name_case_change_does_not_trigger_add_remove():
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
                            "name": "x-api-version",
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

    # No breaking/non-breaking add/remove just due to header casing
    assert result.exit_code() == 0
    assert result.breaking == []
    assert result.non_breaking == []
