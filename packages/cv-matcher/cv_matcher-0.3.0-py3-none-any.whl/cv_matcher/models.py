"""
Data models for CV Matcher library.
"""

from typing import List
from pydantic import BaseModel, Field


class MatchScore(BaseModel):
    """Score representing how well a CV matches a job description."""

    overall_score: float = Field(..., ge=0, le=100, description="Overall match score (0-100)")
    skills_match: float = Field(..., ge=0, le=100, description="Skills match score")
    experience_match: float = Field(..., ge=0, le=100, description="Experience match score")
    education_match: float = Field(..., ge=0, le=100, description="Education match score")
    keywords_match: float = Field(..., ge=0, le=100, description="Keywords match score")

    matching_skills: List[str] = Field(
        default_factory=list, description="Skills that match the job"
    )
    missing_skills: List[str] = Field(default_factory=list, description="Skills missing from CV")
    matching_keywords: List[str] = Field(default_factory=list, description="Keywords found in CV")
    missing_keywords: List[str] = Field(
        default_factory=list, description="Keywords missing from CV"
    )


class FormattingAdvice(BaseModel):
    """Advice on how to improve CV formatting."""

    strengths: List[str] = Field(default_factory=list, description="Strong points of the CV")
    weaknesses: List[str] = Field(default_factory=list, description="Areas needing improvement")
    suggestions: List[str] = Field(
        default_factory=list, description="Specific suggestions for improvement"
    )
    structure_feedback: str = Field(default="", description="Feedback on CV structure")
    content_feedback: str = Field(default="", description="Feedback on CV content")


class CVAnalysis(BaseModel):
    """Complete analysis of a CV against a job description."""

    match_score: MatchScore
    formatting_advice: FormattingAdvice
    summary: str = Field(..., description="Overall summary of the analysis")
    recommendation: str = Field(..., description="Recommendation for the candidate")
