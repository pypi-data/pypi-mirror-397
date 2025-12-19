"""Tests for writer module."""

import csv
import json
import logging
import pytest
from pathlib import Path

from jps_static_audit_utils.finding import Finding
from jps_static_audit_utils.writer import write_text, write_json, write_csv


@pytest.fixture
def sample_findings():
    """Create sample findings for testing."""
    return [
        Finding(
            file="/path/to/script.pl",
            line=10,
            path="/usr/local/bin",
            path_type="absolute",
            context='my $dir = "/usr/local/bin";',
        ),
        Finding(
            file="/path/to/module.pm",
            line=25,
            path="./config/settings.txt",
            path_type="relative",
            context='open(FH, "<", "./config/settings.txt");',
        ),
    ]


@pytest.fixture
def sample_header():
    """Create sample header text for testing."""
    return """Program:        perl-hardcoded-path-report
Version:        1.0.0
Timestamp:      2025-12-17T10:00:00
User:           testuser
Host:           testhost"""


@pytest.fixture
def sample_header_dict():
    """Create sample header dict for testing."""
    return {
        "program": "perl-hardcoded-path-report",
        "version": "1.0.0",
        "timestamp": "2025-12-17T10:00:00",
        "user": "testuser",
        "host": "testhost",
    }


class TestWriteText:
    """Test the write_text function."""

    def test_write_text_creates_file(self, tmp_path, sample_findings, sample_header):
        """Test that write_text creates a report file."""
        report_file = tmp_path / "report.txt"
        
        write_text(sample_findings, sample_header, report_file)
        
        assert report_file.exists()

    def test_write_text_creates_parent_dirs(self, tmp_path, sample_findings, sample_header):
        """Test that write_text creates parent directories."""
        report_file = tmp_path / "nested" / "dir" / "report.txt"
        
        write_text(sample_findings, sample_header, report_file)
        
        assert report_file.exists()

    def test_write_text_contains_header(self, tmp_path, sample_findings, sample_header):
        """Test that the text report contains the header."""
        report_file = tmp_path / "report.txt"
        
        write_text(sample_findings, sample_header, report_file)
        
        content = report_file.read_text()
        assert sample_header in content

    def test_write_text_contains_findings(self, tmp_path, sample_findings, sample_header):
        """Test that the text report contains all findings."""
        report_file = tmp_path / "report.txt"
        
        write_text(sample_findings, sample_header, report_file)
        
        content = report_file.read_text()
        
        for finding in sample_findings:
            assert finding.file in content
            assert str(finding.line) in content
            assert finding.path in content
            assert finding.path_type in content
            assert finding.context in content

    def test_write_text_empty_findings(self, tmp_path, sample_header):
        """Test write_text with empty findings list."""
        report_file = tmp_path / "report.txt"
        
        write_text([], sample_header, report_file)
        
        assert report_file.exists()
        content = report_file.read_text()
        assert sample_header in content


class TestWriteJson:
    """Test the write_json function."""

    def test_write_json_creates_file(self, tmp_path, sample_findings, sample_header_dict):
        """Test that write_json creates a report file."""
        report_file = tmp_path / "report.json"
        
        write_json(sample_findings, sample_header_dict, report_file)
        
        assert report_file.exists()

    def test_write_json_creates_parent_dirs(self, tmp_path, sample_findings, sample_header_dict):
        """Test that write_json creates parent directories."""
        report_file = tmp_path / "nested" / "dir" / "report.json"
        
        write_json(sample_findings, sample_header_dict, report_file)
        
        assert report_file.exists()

    def test_write_json_valid_json(self, tmp_path, sample_findings, sample_header_dict):
        """Test that write_json creates valid JSON."""
        report_file = tmp_path / "report.json"
        
        write_json(sample_findings, sample_header_dict, report_file)
        
        with report_file.open() as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert "header" in data
        assert "findings" in data

    def test_write_json_contains_header(self, tmp_path, sample_findings, sample_header_dict):
        """Test that JSON output contains header information."""
        report_file = tmp_path / "report.json"
        
        write_json(sample_findings, sample_header_dict, report_file)
        
        with report_file.open() as f:
            data = json.load(f)
        
        assert data["header"] == sample_header_dict

    def test_write_json_contains_findings(self, tmp_path, sample_findings, sample_header_dict):
        """Test that JSON output contains all findings."""
        report_file = tmp_path / "report.json"
        
        write_json(sample_findings, sample_header_dict, report_file)
        
        with report_file.open() as f:
            data = json.load(f)
        
        assert len(data["findings"]) == len(sample_findings)
        
        for i, finding in enumerate(sample_findings):
            assert data["findings"][i]["file"] == finding.file
            assert data["findings"][i]["line"] == finding.line
            assert data["findings"][i]["path"] == finding.path
            assert data["findings"][i]["path_type"] == finding.path_type
            assert data["findings"][i]["context"] == finding.context

    def test_write_json_empty_findings(self, tmp_path, sample_header_dict):
        """Test write_json with empty findings list."""
        report_file = tmp_path / "report.json"
        
        write_json([], sample_header_dict, report_file)
        
        with report_file.open() as f:
            data = json.load(f)
        
        assert data["findings"] == []


class TestWriteCsv:
    """Test the write_csv function."""

    def test_write_csv_creates_file(self, tmp_path, sample_findings, sample_header_dict):
        """Test that write_csv creates a report file."""
        report_file = tmp_path / "report.csv"
        
        write_csv(sample_findings, sample_header_dict, report_file)
        
        assert report_file.exists()

    def test_write_csv_creates_parent_dirs(self, tmp_path, sample_findings, sample_header_dict):
        """Test that write_csv creates parent directories."""
        report_file = tmp_path / "nested" / "dir" / "report.csv"
        
        write_csv(sample_findings, sample_header_dict, report_file)
        
        assert report_file.exists()

    def test_write_csv_contains_header_comments(self, tmp_path, sample_findings, sample_header_dict):
        """Test that CSV contains header as comments."""
        report_file = tmp_path / "report.csv"
        
        write_csv(sample_findings, sample_header_dict, report_file)
        
        with report_file.open() as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # First rows should be header comments
        header_rows = [row for row in rows if row and row[0].startswith('#')]
        assert len(header_rows) > 0

    def test_write_csv_contains_column_headers(self, tmp_path, sample_findings, sample_header_dict):
        """Test that CSV contains column headers."""
        report_file = tmp_path / "report.csv"
        
        write_csv(sample_findings, sample_header_dict, report_file)
        
        with report_file.open() as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Find the column header row (first non-comment, non-empty row)
        data_rows = [row for row in rows if row and not row[0].startswith('#')]
        assert len(data_rows) > 0
        
        header_row = data_rows[0]
        assert "file" in header_row
        assert "line" in header_row
        assert "path_type" in header_row
        assert "path" in header_row
        assert "context" in header_row

    def test_write_csv_contains_findings(self, tmp_path, sample_findings, sample_header_dict):
        """Test that CSV contains all findings."""
        report_file = tmp_path / "report.csv"
        
        write_csv(sample_findings, sample_header_dict, report_file)
        
        with report_file.open() as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Get data rows (skip comments and headers)
        data_rows = [row for row in rows if row and not row[0].startswith('#')]
        data_rows = data_rows[1:]  # Skip column headers
        
        assert len(data_rows) == len(sample_findings)
        
        for i, finding in enumerate(sample_findings):
            row = data_rows[i]
            assert finding.file in row
            assert str(finding.line) in row
            assert finding.path_type in row
            assert finding.path in row
            assert finding.context in row

    def test_write_csv_empty_findings(self, tmp_path, sample_header_dict):
        """Test write_csv with empty findings list."""
        report_file = tmp_path / "report.csv"
        
        write_csv([], sample_header_dict, report_file)
        
        assert report_file.exists()
        
        with report_file.open() as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Should still have headers but no data rows
        data_rows = [row for row in rows if row and not row[0].startswith('#')]
        assert len(data_rows) == 1  # Only column headers
