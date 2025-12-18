"""
Tests for job description fetcher module.
"""

import pytest
from cv_matcher.job_fetcher import JobDescriptionFetcher


class TestJobDescriptionFetcher:
    """Tests for JobDescriptionFetcher class."""

    def test_fetch_plain_text(self):
        """Test fetching plain text job description."""
        fetcher = JobDescriptionFetcher()
        text = "Software Engineer position requires Python skills"
        result = fetcher.fetch(text)
        assert result == text.strip()

    def test_is_url_valid(self):
        """Test URL detection with valid URLs."""
        fetcher = JobDescriptionFetcher()
        assert fetcher._is_url("https://example.com/job") is True
        assert fetcher._is_url("http://example.com") is True

    def test_is_url_invalid(self):
        """Test URL detection with invalid URLs."""
        fetcher = JobDescriptionFetcher()
        assert fetcher._is_url("plain text") is False
        assert fetcher._is_url("not a url") is False

    def test_extract_key_info(self):
        """Test extraction of key information from job description."""
        fetcher = JobDescriptionFetcher()
        job_desc = """
        Software Engineer
        
        Requirements:
        - Python
        - Django
        
        Responsibilities:
        - Write code
        - Review PRs
        """
        info = fetcher.extract_key_info(job_desc)
        assert info["has_requirements"] is True
        assert info["has_responsibilities"] is True
        assert info["word_count"] > 0
