from schema_diff.openapi.diff import diff_openapi


def test_components_parameters_ref_is_resolved_and_used():
    old = {
        "openapi": "3.0.0",
        "components": {
            "parameters": {
                "XApiVersion": {
                    "name": "X-API-Version",
                    "in": "header",
                    "required": False,
                    "schema": {"type": "string"},
                }
            }
        },
        "paths": {
            "/users": {
                "get": {
                    "parameters": [{"$ref": "#/components/parameters/XApiVersion"}],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    # Change schema type via the referenced parameter => should be breaking
    new = {
        "openapi": "3.0.0",
        "components": {
            "parameters": {
                "XApiVersion": {
                    "name": "x-api-version",  # casing shouldn't matter for header identity
                    "in": "header",
                    "required": False,
                    "schema": {"type": "integer"},  # type change
                }
            }
        },
        "paths": {
            "/users": {
                "get": {
                    "parameters": [{"$ref": "#/components/parameters/XApiVersion"}],
                    "responses": {"200": {"description": "ok"}},
                }
            }
        },
    }

    result = diff_openapi(old, new)

    assert result.exit_code() == 1
    assert any(
        "parameters.header" in c.path and "schema" in c.path for c in result.breaking
    )
