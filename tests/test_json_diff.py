import os
from tools.json_diff.json_diff import json_diff

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures/json_diff')

def fix(name):
    return os.path.join(FIXTURES_DIR, name)


def test_identical_files():
    result = json_diff(fix('identical.json'), fix('identical.json'))
    assert result["summary"] == {"identical": 4, "different": 0, "missing_in_production": 0, "extra_in_production": 0}
    assert result["different"] == []
    assert result["missing_in_production"] == []
    assert result["extra_in_production"] == []
    assert len(result["identical"]) == 4


def test_value_diff():
    result = json_diff(fix('staging_diff_value.json'), fix('production_diff_value.json'))
    assert result["summary"]["different"] == 1
    assert result["summary"]["identical"] == 3
    diff = result["different"][0]
    assert diff["path"] == "$.role"
    assert diff["status"] == "value_diff"
    assert diff["staging"] == "admin"
    assert diff["production"] == "viewer"


def test_missing_in_production():
    result = json_diff(fix('staging_missing_keys.json'), fix('production_missing_keys.json'))
    assert result["summary"]["missing_in_production"] == 1
    assert result["summary"]["different"] == 0
    assert result["summary"]["identical"] == 4
    entry = result["missing_in_production"][0]
    assert entry["path"] == "$.last_login"
    assert entry["staging"] == "2024-01-15"


def test_missing_and_different():
    result = json_diff(fix('staging_missing_and_diff.json'), fix('production_missing_and_diff.json'))
    assert result["summary"]["missing_in_production"] == 1
    assert result["summary"]["different"] == 1
    assert result["missing_in_production"][0]["path"] == "$.last_login"
    diff = result["different"][0]
    assert diff["path"] == "$.role"
    assert diff["staging"] == "admin"
    assert diff["production"] == "viewer"


def test_empty_production():
    result = json_diff(fix('identical.json'), fix('production_empty.json'))
    assert result["summary"]["missing_in_production"] == 4
    assert result["summary"]["identical"] == 0
    assert result["summary"]["different"] == 0
    assert result["summary"]["extra_in_production"] == 0


def test_extra_keys_in_production():
    result = json_diff(fix('staging_extra_prod_key.json'), fix('production_extra_prod_key.json'))
    assert result["summary"]["extra_in_production"] == 1
    assert result["summary"]["identical"] == 3
    assert result["summary"]["missing_in_production"] == 0
    entry = result["extra_in_production"][0]
    assert entry["path"] == "$.env"
    assert entry["production"] == "production"


def test_type_mismatch():
    result = json_diff(fix('staging_type_mismatch.json'), fix('production_type_mismatch.json'))
    assert result["summary"]["different"] == 1
    diff = result["different"][0]
    assert diff["status"] == "type_mismatch"
    assert diff["path"] == "$.score"
    assert diff["staging_type"] == "int"
    assert diff["production_type"] == "str"
    assert diff["staging"] == 5
    assert diff["production"] == "5"


def test_null_vs_missing_key():
    result = json_diff(fix('staging_null_key.json'), fix('production_null_key.json'))
    assert result["summary"]["missing_in_production"] == 1
    entry = result["missing_in_production"][0]
    assert entry["path"] == "$.last_login"
    assert entry["staging"] is None
    assert entry["note"] == "staging key is explicitly null"


def test_nested_objects():
    result = json_diff(fix('staging_nested.json'), fix('production_nested.json'))
    assert result["summary"]["different"] == 1
    assert result["summary"]["identical"] == 2  # user_id + address.zip
    diff = result["different"][0]
    assert diff["path"] == "$.address.city"
    assert diff["staging"] == "Hanoi"
    assert diff["production"] == "HCMC"


def test_whitespace_diff():
    result = json_diff(fix('staging_whitespace.json'), fix('production_whitespace.json'))
    assert result["summary"]["different"] == 1
    diff = result["different"][0]
    assert diff["status"] == "whitespace_diff"
    assert diff["path"] == "$.role"
    assert diff["staging"] == "admin "
    assert diff["production"] == "admin"


def test_array_order_ignored():
    result = json_diff(fix('staging_array.json'), fix('production_array.json'), ignore_array_order=True)
    assert result["summary"]["different"] == 0
    assert result["summary"]["identical"] == 2  # user_id + tags (sets match)


def test_array_order_sensitive():
    result = json_diff(fix('staging_array.json'), fix('production_array.json'), ignore_array_order=False)
    assert result["summary"]["different"] == 2  # tags[0] and tags[2] differ
    assert result["summary"]["identical"] == 2  # user_id + tags[1]
