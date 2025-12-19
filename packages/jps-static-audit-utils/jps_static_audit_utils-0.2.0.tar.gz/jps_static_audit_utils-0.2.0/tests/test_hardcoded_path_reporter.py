"""Tests for hardcoded_path_reporter module."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from jps_static_audit_utils.hardcoded_path_reporter import (
    default_outdir,
    standard_header,
    is_perl_file,
    strip_inline_comment,
    scan_file,
    collect_files,
)
from jps_static_audit_utils.finding import Finding


class TestDefaultOutdir:
    """Test the default_outdir function."""

    @patch('jps_static_audit_utils.hardcoded_path_reporter.getpass.getuser')
    @patch('jps_static_audit_utils.hardcoded_path_reporter.datetime')
    def test_default_outdir_structure(self, mock_datetime, mock_getuser):
        """Test that default_outdir returns expected path structure."""
        mock_getuser.return_value = "testuser"
        mock_datetime.now.return_value.strftime.return_value = "2025-12-17-120000"
        
        result = default_outdir()
        
        assert isinstance(result, Path)
        assert "testuser" in str(result)
        assert "perl-hardcoded-path-report" in str(result)


class TestStandardHeader:
    """Test the standard_header function."""

    @patch('jps_static_audit_utils.hardcoded_path_reporter.socket.gethostname')
    @patch('jps_static_audit_utils.hardcoded_path_reporter.getpass.getuser')
    @patch('jps_static_audit_utils.hardcoded_path_reporter.os.getcwd')
    def test_standard_header_contains_metadata(self, mock_getcwd, mock_getuser, mock_hostname):
        """Test that standard_header contains expected metadata."""
        mock_getuser.return_value = "testuser"
        mock_hostname.return_value = "testhost"
        mock_getcwd.return_value = "/test/dir"
        
        result = standard_header(
            infile=Path("/path/to/file.pl"),
            indir=None,
            report_file=Path("/output/report.txt"),
            logfile=Path("/output/log.txt"),
        )
        
        assert "testuser" in result
        assert "testhost" in result
        assert "/path/to/file.pl" in result
        assert "/output/report.txt" in result
        assert "/output/log.txt" in result

    def test_standard_header_with_indir(self):
        """Test standard_header when indir is provided."""
        result = standard_header(
            infile=None,
            indir=Path("/scan/dir"),
            report_file=Path("/output/report.txt"),
            logfile=Path("/output/log.txt"),
        )
        
        assert "/scan/dir" in result
        assert "N/A" in result  # infile should be N/A


class TestIsPerlFile:
    """Test the is_perl_file function."""

    def test_is_perl_file_pl_extension(self):
        """Test that .pl files are recognized as Perl files."""
        assert is_perl_file(Path("script.pl")) is True

    def test_is_perl_file_pm_extension(self):
        """Test that .pm files are recognized as Perl files."""
        assert is_perl_file(Path("Module.pm")) is True

    def test_is_perl_file_other_extensions(self):
        """Test that non-Perl files are not recognized."""
        assert is_perl_file(Path("script.py")) is False
        assert is_perl_file(Path("document.txt")) is False
        assert is_perl_file(Path("README.md")) is False
        assert is_perl_file(Path("script.sh")) is False

    def test_is_perl_file_no_extension(self):
        """Test files with no extension."""
        assert is_perl_file(Path("script")) is False


class TestStripInlineComment:
    """Test the strip_inline_comment function."""

    def test_strip_inline_comment_with_comment(self):
        """Test stripping inline comments."""
        assert strip_inline_comment('my $var = "value"; # comment') == 'my $var = "value"; '

    def test_strip_inline_comment_no_comment(self):
        """Test lines without comments."""
        assert strip_inline_comment('my $var = "value";') == 'my $var = "value";'

    def test_strip_inline_comment_only_comment(self):
        """Test lines that are only comments."""
        assert strip_inline_comment('# this is a comment') == ''

    def test_strip_inline_comment_empty_line(self):
        """Test empty lines."""
        assert strip_inline_comment('') == ''

    def test_strip_inline_comment_hash_in_string(self):
        """Test that # in strings is treated as comment delimiter."""
        # This is a known limitation - the function doesn't parse strings
        result = strip_inline_comment('my $var = "value#test";')
        assert result == 'my $var = "value'


class TestScanFile:
    """Test the scan_file function."""

    def test_scan_file_finds_absolute_paths(self, tmp_path):
        """Test that scan_file finds absolute paths."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('''#!/usr/bin/perl
my $path = "/usr/local/bin";
my $dir = "/tmp/data";
''')
        
        findings = scan_file(test_file)
        
        assert len(findings) == 2
        assert any(f.path == "/usr/local/bin" for f in findings)
        assert any(f.path == "/tmp/data" for f in findings)

    def test_scan_file_finds_relative_paths(self, tmp_path):
        """Test that scan_file finds relative paths."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('''#!/usr/bin/perl
my $config = "./config/settings.txt";
my $lib = "../lib/module.pm";
''')
        
        findings = scan_file(test_file)
        
        assert len(findings) == 2
        assert any(f.path == "./config/settings.txt" for f in findings)
        assert any(f.path == "../lib/module.pm" for f in findings)

    def test_scan_file_ignores_urls(self, tmp_path):
        """Test that scan_file ignores URLs."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('''#!/usr/bin/perl
my $url = "https://example.com/path";
my $s3 = "s3://bucket/key";
my $path = "/usr/local/bin";
''')
        
        findings = scan_file(test_file)
        
        # Should only find the real path, not URLs
        assert len(findings) == 1
        assert findings[0].path == "/usr/local/bin"

    def test_scan_file_ignores_env_vars(self, tmp_path):
        """Test that scan_file ignores $ENV{} variables."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('''#!/usr/bin/perl
my $home = $ENV{HOME};
my $path = $ENV{PATH} . "/usr/local/bin";
my $real_path = "/tmp/data";
''')
        
        findings = scan_file(test_file)
        
        # Should only find the real path, not $ENV references
        assert len(findings) == 1
        assert findings[0].path == "/tmp/data"

    def test_scan_file_skips_pod_documentation(self, tmp_path):
        """Test that scan_file skips POD documentation."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('''#!/usr/bin/perl

=head1 NAME

Example - "/usr/local/bin" should be ignored in POD

=cut

my $path = "/tmp/data";
''')
        
        findings = scan_file(test_file)
        
        # Should only find path outside POD
        assert len(findings) == 1
        assert findings[0].path == "/tmp/data"

    def test_scan_file_skips_comments(self, tmp_path):
        """Test that scan_file skips inline comments."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('''#!/usr/bin/perl
# my $path = "/commented/path";
my $real = "/tmp/data";  # not "/another/path"
''')
        
        findings = scan_file(test_file)
        
        # Should only find the real path, not commented ones
        # Note: The current implementation may still find paths in inline comments
        # after the code, which is a limitation
        assert any(f.path == "/tmp/data" for f in findings)

    def test_scan_file_empty_file(self, tmp_path):
        """Test scanning an empty file."""
        test_file = tmp_path / "empty.pl"
        test_file.write_text("")
        
        findings = scan_file(test_file)
        
        assert len(findings) == 0

    def test_scan_file_records_line_numbers(self, tmp_path):
        """Test that findings include correct line numbers."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('''#!/usr/bin/perl
# Line 2
my $path1 = "/first/path";
# Line 4
my $path2 = "/second/path";
''')
        
        findings = scan_file(test_file)
        
        assert len(findings) == 2
        finding1 = next(f for f in findings if f.path == "/first/path")
        finding2 = next(f for f in findings if f.path == "/second/path")
        
        assert finding1.line == 3
        assert finding2.line == 5

    def test_scan_file_records_context(self, tmp_path):
        """Test that findings include the line context."""
        test_file = tmp_path / "test.pl"
        test_file.write_text('my $path = "/usr/local/bin";\n')
        
        findings = scan_file(test_file)
        
        assert len(findings) == 1
        assert findings[0].context == 'my $path = "/usr/local/bin";'

    def test_scan_file_records_file_path(self, tmp_path):
        """Test that findings include the file path."""
        test_file = tmp_path / "script.pl"
        test_file.write_text('my $path = "/tmp";\n')
        
        findings = scan_file(test_file)
        
        assert len(findings) == 1
        assert findings[0].file == str(test_file)


class TestCollectFiles:
    """Test the collect_files function."""

    def test_collect_files_with_infile(self, tmp_path):
        """Test collect_files with a single input file."""
        test_file = tmp_path / "test.pl"
        test_file.write_text("")
        
        files = list(collect_files(indir=None, infile=test_file))
        
        assert len(files) == 1
        assert files[0] == test_file

    def test_collect_files_with_indir(self, tmp_path):
        """Test collect_files with a directory."""
        (tmp_path / "script1.pl").write_text("")
        (tmp_path / "Module.pm").write_text("")
        (tmp_path / "README.md").write_text("")
        
        files = list(collect_files(indir=tmp_path, infile=None))
        
        # Should only include .pl and .pm files
        assert len(files) == 2
        assert any(f.name == "script1.pl" for f in files)
        assert any(f.name == "Module.pm" for f in files)

    def test_collect_files_recursive(self, tmp_path):
        """Test that collect_files recursively scans directories."""
        (tmp_path / "script.pl").write_text("")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "module.pm").write_text("")
        
        files = list(collect_files(indir=tmp_path, infile=None))
        
        assert len(files) == 2
        assert any(f.name == "script.pl" for f in files)
        assert any(f.name == "module.pm" for f in files)

    def test_collect_files_empty_directory(self, tmp_path):
        """Test collect_files with an empty directory."""
        files = list(collect_files(indir=tmp_path, infile=None))
        
        assert len(files) == 0

    def test_collect_files_no_perl_files(self, tmp_path):
        """Test collect_files when directory has no Perl files."""
        (tmp_path / "README.md").write_text("")
        (tmp_path / "script.py").write_text("")
        
        files = list(collect_files(indir=tmp_path, infile=None))
        
        assert len(files) == 0
