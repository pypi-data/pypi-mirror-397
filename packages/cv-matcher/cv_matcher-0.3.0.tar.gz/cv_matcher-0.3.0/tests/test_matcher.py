"""
Tests for CVMatcher main class.
"""

import pytest
from unittest.mock import Mock, patch
from cv_matcher import CVMatcher
from cv_matcher.models import CVAnalysis, MatchScore, FormattingAdvice


class TestCVMatcher:
    """Tests for CVMatcher class."""

    def test_init_no_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises((ValueError, ImportError)):
                CVMatcher(use_local_model=False)

    def test_init_with_api_key(self):
        """Test successful initialization with API key."""
        with patch("cv_matcher.matcher.AIAnalyzer"):
            matcher = CVMatcher(use_local_model=False, api_key="test-key")
            assert matcher is not None

    def test_get_score_color(self):
        """Test score color determination."""
        with patch("cv_matcher.matcher.AIAnalyzer"):
            matcher = CVMatcher(use_local_model=False, api_key="test-key")
            assert matcher._get_score_color(85) == "green"
            assert matcher._get_score_color(65) == "yellow"
            assert matcher._get_score_color(45) == "orange"
            assert matcher._get_score_color(25) == "red"

    @patch("cv_matcher.matcher.AIAnalyzer")
    @patch("cv_matcher.matcher.PDFParser.extract_text")
    @patch("cv_matcher.matcher.JobDescriptionFetcher.fetch")
    def test_analyze_cv_success(self, mock_fetch, mock_extract, mock_ai_analyzer):
        """Test successful CV analysis."""
        # Setup mocks
        mock_extract.return_value = "CV content"
        mock_fetch.return_value = "Job description"

        mock_score = MatchScore(
            overall_score=75.0,
            skills_match=80.0,
            experience_match=70.0,
            education_match=65.0,
            keywords_match=85.0,
        )
        mock_advice = FormattingAdvice(
            strengths=["Good"], weaknesses=["Improve"], suggestions=["Add more"]
        )
        mock_analysis = CVAnalysis(
            match_score=mock_score,
            formatting_advice=mock_advice,
            summary="Good match",
            recommendation="Apply",
        )

        # Mock the analyzer instance and its analyze method
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = mock_analysis
        mock_ai_analyzer.return_value = mock_analyzer_instance

        # Test
        matcher = CVMatcher(use_local_model=False, api_key="test-key")
        result = matcher.analyze_cv("test.pdf", "job description")

        assert result.match_score.overall_score == 75.0
        assert result.summary == "Good match"
        mock_extract.assert_called_once()
        mock_fetch.assert_called_once()
        mock_analyzer_instance.analyze.assert_called_once()
