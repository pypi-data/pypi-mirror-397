"""Tests for logging_helper module."""

import logging
import pytest
from pathlib import Path

from jps_static_audit_utils.logging_helper import setup_logging


class TestSetupLogging:
    """Test the setup_logging function."""

    def test_setup_logging_creates_logfile(self, tmp_path):
        """Test that setup_logging creates the log file."""
        logfile = tmp_path / "test.log"
        
        setup_logging(logfile)
        
        assert logfile.exists()

    def test_setup_logging_creates_parent_directories(self, tmp_path):
        """Test that setup_logging creates parent directories if they don't exist."""
        logfile = tmp_path / "subdir" / "nested" / "test.log"
        
        setup_logging(logfile)
        
        assert logfile.parent.exists()
        assert logfile.exists()

    def test_setup_logging_configures_logger(self, tmp_path):
        """Test that setup_logging configures the root logger."""
        logfile = tmp_path / "test.log"
        
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()
        
        setup_logging(logfile)
        
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 2  # File and stderr handlers

    def test_setup_logging_file_handler(self, tmp_path):
        """Test that a file handler is added and logs to file."""
        logfile = tmp_path / "test.log"
        
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()
        
        setup_logging(logfile)
        
        # Log a test message
        test_message = "Test log message"
        logging.info(test_message)
        
        # Check that the message was written to the file
        log_content = logfile.read_text()
        assert test_message in log_content

    def test_setup_logging_file_handler_format(self, tmp_path):
        """Test that file handler uses the correct format."""
        logfile = tmp_path / "test.log"
        
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()
        
        setup_logging(logfile)
        
        # Log a test message
        logging.info("Test message")
        
        # Check log format contains expected fields
        log_content = logfile.read_text()
        assert "INFO" in log_content
        assert ":" in log_content

    def test_setup_logging_stderr_handler_exists(self, tmp_path):
        """Test that a stderr handler is configured."""
        logfile = tmp_path / "test.log"
        
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()
        
        setup_logging(logfile)
        
        # Find the StreamHandler
        stderr_handlers = [
            h for h in logger.handlers 
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        ]
        
        assert len(stderr_handlers) >= 1
        assert stderr_handlers[0].level == logging.WARNING

    def test_setup_logging_multiple_calls(self, tmp_path):
        """Test that multiple calls to setup_logging don't create duplicate handlers."""
        logfile1 = tmp_path / "test1.log"
        logfile2 = tmp_path / "test2.log"
        
        # Clear any existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()
        
        setup_logging(logfile1)
        initial_handler_count = len(logger.handlers)
        
        setup_logging(logfile2)
        final_handler_count = len(logger.handlers)
        
        # Each call adds 2 handlers (file + stderr)
        assert final_handler_count == initial_handler_count + 2

    def test_setup_logging_with_existing_file(self, tmp_path):
        """Test setup_logging when log file already exists."""
        logfile = tmp_path / "existing.log"
        logfile.write_text("Existing content\n")
        
        setup_logging(logfile)
        
        # Log a new message
        logging.info("New message")
        
        log_content = logfile.read_text()
        assert "New message" in log_content
