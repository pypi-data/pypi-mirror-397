"""
CV Matcher - AI-powered CV analysis and job matching library.
"""

__version__ = "0.1.0"

from cv_matcher.matcher import CVMatcher
from cv_matcher.models import CVAnalysis, MatchScore, FormattingAdvice

__all__ = ["CVMatcher", "CVAnalysis", "MatchScore", "FormattingAdvice", "launch_ui"]


def launch_ui(*args, **kwargs):
    """
    Launch the Gradio web UI for CV Matcher.
    This is a lazy import to avoid loading Gradio when not needed.
    """
    from cv_matcher.ui import launch_ui as _launch_ui

    return _launch_ui(*args, **kwargs)
