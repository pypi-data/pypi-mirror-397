#!/usr/bin/env python3
"""Unit tests for constants module."""
from __future__ import annotations

from pathlib import Path

from jps_ado_pr_utils.constants import (
    API_VERSION,
    DEFAULT_ENV_FILE,
    LOGGING_FORMAT,
    ORG,
)


class TestConstants:
    """Test module constants."""

    def test_org_defined(self):
        """Test ORG constant is defined."""
        assert isinstance(ORG, str)
        assert len(ORG) > 0

    def test_api_version_defined(self):
        """Test API_VERSION constant is defined."""
        assert isinstance(API_VERSION, str)
        assert len(API_VERSION) > 0

    def test_logging_format_defined(self):
        """Test LOGGING_FORMAT constant is defined."""
        assert isinstance(LOGGING_FORMAT, str)
        assert "%" in LOGGING_FORMAT

    def test_default_env_file_is_path(self):
        """Test DEFAULT_ENV_FILE is a Path object."""
        assert isinstance(DEFAULT_ENV_FILE, Path)

    def test_default_env_file_expanduser(self):
        """Test DEFAULT_ENV_FILE path is expanded."""
        assert "~" not in str(DEFAULT_ENV_FILE)
