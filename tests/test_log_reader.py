import os
from tools.log_monitor.log_reader import log_reader

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures/log_monitor')


def test_parse_log_counts_errors():
    result = log_reader(os.path.join(FIXTURES_DIR, 'sample_errors.log'))
    assert result["Database connection failed: timeout"] == 20
    assert result["Auth service unreachable"] == 1


def test_parse_log_handles_no_errors():
    result = log_reader(os.path.join(FIXTURES_DIR, 'no_errors.log'))
    assert result == {}


def test_parse_log_handles_empty_error_message():
    result = log_reader(os.path.join(FIXTURES_DIR, 'empty_error_message.log'))
    assert result == {
        "Unknown error": 3,
    }

def test_parse_log_handles_nonexistent_file():
    result = log_reader(os.path.join(FIXTURES_DIR, 'nonexistent.log'))
    assert result == "File not found: " + os.path.join(FIXTURES_DIR, 'nonexistent.log')


def test_parse_log_handles_empty_file():
    result = log_reader(os.path.join(FIXTURES_DIR, 'empty_file.log'))
    assert result == {}
