from schema_diff.diff import diff_objects
from schema_diff.models import ChangeType


def _types(changes):
    return [c.change_type for c in changes]


def test_removed_field_is_breaking():
    old = {"User": {"email": "a@b.com", "age": 30}}
    new = {"User": {"age": 30}}

    result = diff_objects(old, new)

    assert result.has_breaking_changes() is True
    assert result.exit_code() == 1
    assert any(
        c.change_type == ChangeType.REMOVED_FIELD and c.path == "User.email"
        for c in result.breaking
    )


def test_added_field_is_non_breaking():
    old = {"User": {"age": 30}}
    new = {"User": {"age": 30, "email": "a@b.com"}}

    result = diff_objects(old, new)

    assert result.has_breaking_changes() is False
    assert result.exit_code() == 0
    assert any(
        c.change_type == ChangeType.ADDED_FIELD and c.path == "User.email"
        for c in result.non_breaking
    )


def test_type_change_is_breaking_top_level():
    old = {"amount": 12.5}
    new = {"amount": "12.5"}

    result = diff_objects(old, new)

    assert result.has_breaking_changes() is True
    assert any(
        c.change_type == ChangeType.TYPE_CHANGE
        and c.path == "amount"
        and c.old_type in ("float", "int")  # depends on input
        and c.new_type == "str"
        for c in result.breaking
    )


def test_type_change_is_breaking_nested():
    old = {"Order": {"amount": 12.5}}
    new = {"Order": {"amount": "12.5"}}

    result = diff_objects(old, new)

    assert result.has_breaking_changes() is True
    assert any(
        c.change_type == ChangeType.TYPE_CHANGE
        and c.path == "Order.amount"
        and c.new_type == "str"
        for c in result.breaking
    )


def test_list_element_type_change_is_breaking_when_both_non_empty():
    old = {"items": [{"id": 1}]}
    new = {"items": ["oops"]}

    result = diff_objects(old, new)

    # Your MVP list rule compares first element types
    assert result.has_breaking_changes() is True
    assert any(
        c.change_type == ChangeType.TYPE_CHANGE
        and c.path in ("items[]", "items.[]", "items[]")  # we use "items[]"
        for c in result.breaking
    )


def test_no_changes():
    old = {"User": {"age": 30}, "tags": [1, 2, 3]}
    new = {"User": {"age": 30}, "tags": [1, 2, 3]}

    result = diff_objects(old, new)

    assert result.has_breaking_changes() is False
    assert result.exit_code() == 0
    assert result.breaking == []
    # non_breaking might still be empty; this is expected
    assert result.non_breaking == []
