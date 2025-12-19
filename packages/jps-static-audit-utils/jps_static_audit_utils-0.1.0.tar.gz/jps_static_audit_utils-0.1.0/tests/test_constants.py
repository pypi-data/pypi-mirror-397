"""Tests for constants module."""

import re
import pytest

from jps_static_audit_utils.constants import (
    ABS_PATH_RE,
    REL_PATH_RE,
    URL_RE,
    ENV_RE,
    LOGGING_FORMAT,
    PROGRAM_NAME,
    PROGRAM_VERSION,
    TIMESTAMP_FMT,
)


class TestRegexPatterns:
    """Test regex patterns for path detection."""

    def test_abs_path_re_matches_valid_paths(self):
        """Test that ABS_PATH_RE matches valid absolute paths."""
        test_cases = [
            ('"/usr/local/bin"', '/usr/local/bin'),
            ("'/home/user/file.txt'", '/home/user/file.txt'),
            ('"/tmp/test"', '/tmp/test'),
            ("'/opt/app/config'", '/opt/app/config'),
            ('"/var/log/app.log"', '/var/log/app.log'),
        ]
        
        for input_str, expected_path in test_cases:
            match = ABS_PATH_RE.search(input_str)
            assert match is not None, f"Failed to match: {input_str}"
            assert match.group(2) == expected_path

    def test_abs_path_re_no_match_relative_paths(self):
        """Test that ABS_PATH_RE doesn't match relative paths."""
        test_cases = [
            '"./relative/path"',
            '"../parent/path"',
            '"relative/path"',
            '""',
        ]
        
        for input_str in test_cases:
            match = ABS_PATH_RE.search(input_str)
            assert match is None, f"Should not match: {input_str}"

    def test_rel_path_re_matches_valid_relative_paths(self):
        """Test that REL_PATH_RE matches valid relative paths."""
        test_cases = [
            ('"./config/file.txt"', './config/file.txt'),
            ("'../parent/dir'", '../parent/dir'),
            ('"./../mixed"', './../mixed'),
            ('"./file"', './file'),
            ('"../file"', '../file'),
        ]
        
        for input_str, expected_path in test_cases:
            match = REL_PATH_RE.search(input_str)
            assert match is not None, f"Failed to match: {input_str}"
            assert match.group(2) == expected_path

    def test_rel_path_re_no_match_absolute_paths(self):
        """Test that REL_PATH_RE doesn't match absolute paths."""
        test_cases = [
            '"/usr/local/bin"',
            '"/tmp/test"',
            '"relative"',  # Not starting with ./ or ../
            '""',
        ]
        
        for input_str in test_cases:
            match = REL_PATH_RE.search(input_str)
            assert match is None, f"Should not match: {input_str}"

    def test_url_re_matches_valid_urls(self):
        """Test that URL_RE matches various URL schemes."""
        test_cases = [
            'https://example.com',
            'http://localhost:8080',
            's3://bucket/key',
            'gs://bucket/object',
            'ftp://ftp.example.com',
        ]
        
        for url in test_cases:
            match = URL_RE.match(url)
            assert match is not None, f"Failed to match: {url}"

    def test_url_re_no_match_non_urls(self):
        """Test that URL_RE doesn't match non-URL strings."""
        test_cases = [
            '/usr/local/bin',
            './relative/path',
            'file://path',
            'example.com',
        ]
        
        for input_str in test_cases:
            match = URL_RE.match(input_str)
            assert match is None, f"Should not match: {input_str}"

    def test_env_re_matches_perl_env_vars(self):
        """Test that ENV_RE matches Perl environment variable syntax."""
        test_cases = [
            '$ENV{HOME}',
            '$ENV{PATH}',
            '$ENV{USER_NAME}',
            '$ENV{MY_VAR_123}',
        ]
        
        for env_var in test_cases:
            match = ENV_RE.search(env_var)
            assert match is not None, f"Failed to match: {env_var}"

    def test_env_re_no_match_other_vars(self):
        """Test that ENV_RE doesn't match other variable syntaxes."""
        test_cases = [
            '$var',
            '${var}',
            '$ENV',
            'ENV{HOME}',
        ]
        
        for input_str in test_cases:
            match = ENV_RE.search(input_str)
            assert match is None, f"Should not match: {input_str}"


class TestConstants:
    """Test constant values."""

    def test_logging_format_contains_required_fields(self):
        """Test that LOGGING_FORMAT contains expected fields."""
        assert 'levelname' in LOGGING_FORMAT
        assert 'asctime' in LOGGING_FORMAT
        assert 'pathname' in LOGGING_FORMAT
        assert 'lineno' in LOGGING_FORMAT
        assert 'message' in LOGGING_FORMAT

    def test_program_name_is_string(self):
        """Test that PROGRAM_NAME is a non-empty string."""
        assert isinstance(PROGRAM_NAME, str)
        assert len(PROGRAM_NAME) > 0

    def test_program_version_is_string(self):
        """Test that PROGRAM_VERSION is a non-empty string."""
        assert isinstance(PROGRAM_VERSION, str)
        assert len(PROGRAM_VERSION) > 0

    def test_timestamp_fmt_is_valid(self):
        """Test that TIMESTAMP_FMT is a valid datetime format string."""
        from datetime import datetime
        
        # Should not raise an exception
        timestamp = datetime.now().strftime(TIMESTAMP_FMT)
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0
