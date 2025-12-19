# jps-static-audit-utils

![Build](https://github.com/jai-python3/jps-static-audit-utils/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-static-audit-utils/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-static-audit-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-static-audit-utils)

Collection of Python utilities for static code analysis on Perl, Python, and R scripts.

## 🚀 Overview

`jps-static-audit-utils` provides tools for performing read-only static analysis on codebases, particularly focusing on detecting hardcoded file and directory paths in Perl scripts. This can help identify potential security issues, portability problems, and maintainability concerns in legacy code.

### Features

- **Hardcoded Path Detection**: Scans Perl files (.pl, .pm) for absolute and relative file/directory paths
- **Smart Filtering**: Automatically excludes URLs, environment variables, and POD documentation
- **Multiple Output Formats**: Generate reports in text, JSON, or CSV format
- **Recursive Scanning**: Scan entire directory trees or individual files
- **Detailed Reporting**: Each finding includes file path, line number, path type, and context
- **Comprehensive Testing**: Full test suite with pytest ensuring reliability

### Example Usage

#### Scan a Single Perl File

```bash
# Scan a single file and generate a text report
jps-bootstrap scan --infile /path/to/script.pl

# Specify output format (text, json, or csv)
jps-bootstrap scan --infile script.pl --format json
```

#### Scan a Directory Recursively

```bash
# Scan all Perl files in a directory
jps-bootstrap scan --indir /path/to/perl/project

# Specify custom output directory
jps-bootstrap scan --indir /path/to/project --outdir /path/to/output
```

#### Custom Report Location

```bash
# Specify exact report file location
jps-bootstrap scan --infile script.pl --report-file /custom/path/report.txt --logfile /custom/path/scan.log
```

### What Gets Detected

The scanner identifies:

- **Absolute paths**: `/usr/local/bin`, `/tmp/data`, `/var/log/app.log`
- **Relative paths**: `./config/settings.txt`, `../lib/module.pm`

The scanner intelligently ignores:

- **URLs**: `https://example.com/path`, `s3://bucket/key`
- **Environment variables**: `$ENV{HOME}`, `$ENV{PATH}`
- **POD documentation**: Paths mentioned in Perl documentation blocks

### Output Formats

#### Text Report
```
File:    /path/to/script.pl
Line:    42
Type:    absolute
Path:    /usr/local/bin
Context: my $path = "/usr/local/bin";
```

#### JSON Report
```json
{
  "header": {
    "program": "perl-hardcoded-path-report",
    "version": "1.0.0",
    "timestamp": "2025-12-17T10:00:00"
  },
  "findings": [
    {
      "file": "/path/to/script.pl",
      "line": 42,
      "path": "/usr/local/bin",
      "path_type": "absolute",
      "context": "my $path = \"/usr/local/bin\";"
    }
  ]
}
```

#### CSV Report
```csv
file,line,path_type,path,context
/path/to/script.pl,42,absolute,/usr/local/bin,"my $path = ""/usr/local/bin"";"
```

## 📦 Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/jai-python3/jps-static-audit-utils.git
cd jps-static-audit-utils

# Install the package
make install
```

### For Development

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

## 🧪 Development

### Running Tests

```bash
# Run all tests with pytest
make test

# Run tests with coverage
pytest --cov=src/jps_static_audit_utils --cov-report=html tests/

# Run specific test file
pytest tests/test_hardcoded_path_reporter.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Fix auto-fixable issues
make fix

# Run all quality checks
make fix && make format && make lint
```

### Project Structure

```
jps-static-audit-utils/
├── src/
│   └── jps_static_audit_utils/
│       ├── __init__.py
│       ├── constants.py              # Regex patterns and constants
│       ├── finding.py                # Finding dataclass
│       ├── hardcoded_path_reporter.py # Main scanning logic
│       ├── logging_helper.py         # Logging configuration
│       └── writer.py                 # Report writers (text/json/csv)
├── tests/
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_constants.py             # Tests for regex patterns
│   ├── test_finding.py               # Tests for Finding dataclass
│   ├── test_hardcoded_path_reporter.py # Tests for scanner
│   ├── test_logging_helper.py        # Tests for logging setup
│   └── test_writer.py                # Tests for report writers
├── pyproject.toml                    # Project configuration
├── Makefile                          # Build and development tasks
└── README.md                         # This file
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters (`make test && make lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 Requirements

- Python 3.10 or higher
- Dependencies listed in [pyproject.toml](pyproject.toml)

## 📜 License

MIT License © Jaideep Sundaram

## 🔗 Links

- [GitHub Repository](https://github.com/jai-python3/jps-static-audit-utils)
- [Issue Tracker](https://github.com/jai-python3/jps-static-audit-utils/issues)
