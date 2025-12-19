"""Tests for Finding dataclass."""

import pytest
from dataclasses import asdict

from jps_static_audit_utils.finding import Finding


class TestFinding:
    """Test the Finding dataclass."""

    def test_finding_creation(self):
        """Test that a Finding can be created with all fields."""
        finding = Finding(
            file="/path/to/file.pl",
            line=42,
            path="/usr/local/bin",
            path_type="absolute",
            context='my $path = "/usr/local/bin";',
        )
        
        assert finding.file == "/path/to/file.pl"
        assert finding.line == 42
        assert finding.path == "/usr/local/bin"
        assert finding.path_type == "absolute"
        assert finding.context == 'my $path = "/usr/local/bin";'

    def test_finding_equality(self):
        """Test that two Findings with same values are equal."""
        finding1 = Finding(
            file="test.pl",
            line=10,
            path="/tmp",
            path_type="absolute",
            context="test",
        )
        finding2 = Finding(
            file="test.pl",
            line=10,
            path="/tmp",
            path_type="absolute",
            context="test",
        )
        
        assert finding1 == finding2

    def test_finding_inequality(self):
        """Test that Findings with different values are not equal."""
        finding1 = Finding(
            file="test.pl",
            line=10,
            path="/tmp",
            path_type="absolute",
            context="test",
        )
        finding2 = Finding(
            file="test.pl",
            line=11,  # Different line
            path="/tmp",
            path_type="absolute",
            context="test",
        )
        
        assert finding1 != finding2

    def test_finding_asdict(self):
        """Test that a Finding can be converted to a dictionary."""
        finding = Finding(
            file="script.pl",
            line=5,
            path="./config",
            path_type="relative",
            context='open(my $fh, "<", "./config");',
        )
        
        result = asdict(finding)
        
        assert isinstance(result, dict)
        assert result["file"] == "script.pl"
        assert result["line"] == 5
        assert result["path"] == "./config"
        assert result["path_type"] == "relative"
        assert result["context"] == 'open(my $fh, "<", "./config");'

    def test_finding_with_special_characters(self):
        """Test Finding with special characters in strings."""
        finding = Finding(
            file="/path/with spaces/file.pl",
            line=1,
            path="/tmp/file with spaces.txt",
            path_type="absolute",
            context='my $file = "/tmp/file with spaces.txt";',
        )
        
        assert " " in finding.file
        assert " " in finding.path
        assert " " in finding.context

    def test_finding_with_empty_context(self):
        """Test Finding with empty context string."""
        finding = Finding(
            file="test.pl",
            line=100,
            path="/var/log",
            path_type="absolute",
            context="",
        )
        
        assert finding.context == ""

    def test_finding_path_types(self):
        """Test different path_type values."""
        absolute_finding = Finding(
            file="test.pl",
            line=1,
            path="/absolute/path",
            path_type="absolute",
            context="test",
        )
        relative_finding = Finding(
            file="test.pl",
            line=2,
            path="./relative/path",
            path_type="relative",
            context="test",
        )
        
        assert absolute_finding.path_type == "absolute"
        assert relative_finding.path_type == "relative"
