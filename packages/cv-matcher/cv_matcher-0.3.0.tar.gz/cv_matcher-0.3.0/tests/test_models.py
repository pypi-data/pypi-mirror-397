"""
Tests for data models.
"""

import pytest
from cv_matcher.models import MatchScore, FormattingAdvice, CVAnalysis


class TestMatchScore:
    """Tests for MatchScore model."""

    def test_match_score_valid(self):
        """Test valid match score creation."""
        score = MatchScore(
            overall_score=75.0,
            skills_match=80.0,
            experience_match=70.0,
            education_match=65.0,
            keywords_match=85.0,
            matching_skills=["Python", "Django"],
            missing_skills=["Docker"],
            matching_keywords=["API", "REST"],
            missing_keywords=["Kubernetes"],
        )
        assert score.overall_score == 75.0
        assert len(score.matching_skills) == 2

    def test_match_score_invalid_range(self):
        """Test that scores must be in 0-100 range."""
        with pytest.raises(ValueError):
            MatchScore(
                overall_score=150.0,  # Invalid: > 100
                skills_match=80.0,
                experience_match=70.0,
                education_match=65.0,
                keywords_match=85.0,
            )


class TestFormattingAdvice:
    """Tests for FormattingAdvice model."""

    def test_formatting_advice_valid(self):
        """Test valid formatting advice creation."""
        advice = FormattingAdvice(
            strengths=["Clear structure", "Good formatting"],
            weaknesses=["Too long"],
            suggestions=["Reduce to 2 pages"],
            structure_feedback="Well organized",
            content_feedback="Strong content",
        )
        assert len(advice.strengths) == 2
        assert advice.structure_feedback == "Well organized"


class TestCVAnalysis:
    """Tests for CVAnalysis model."""

    def test_cv_analysis_valid(self):
        """Test valid CV analysis creation."""
        score = MatchScore(
            overall_score=75.0,
            skills_match=80.0,
            experience_match=70.0,
            education_match=65.0,
            keywords_match=85.0,
        )
        advice = FormattingAdvice(
            strengths=["Good structure"], weaknesses=["Needs work"], suggestions=["Improve summary"]
        )
        analysis = CVAnalysis(
            match_score=score,
            formatting_advice=advice,
            summary="Good match overall",
            recommendation="Apply with confidence",
        )
        assert analysis.match_score.overall_score == 75.0
        assert "Good match" in analysis.summary
