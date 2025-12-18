"""
AI analyzer for matching CVs with job descriptions using OpenAI.
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv
from cv_matcher.models import CVAnalysis, MatchScore, FormattingAdvice

# Load environment variables from .env file
load_dotenv()

# Import OpenAI only when needed
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIAnalyzer:
    """Analyze CVs and job descriptions using AI."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the AI analyzer.

        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY environment variable)
            model: OpenAI model to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is not installed. Install it with: "
                "pip install openai\n"
                "Or use local models instead: CVMatcher(use_local_model=True)"
            )

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Provide it via api_key parameter, "
                "set OPENAI_API_KEY environment variable, or add it to a .env file."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def analyze(self, cv_text: str, job_description: str) -> CVAnalysis:
        """
        Analyze CV against job description.

        Args:
            cv_text: Extracted CV text
            job_description: Job description text

        Returns:
            CVAnalysis object with match score and formatting advice
        """
        prompt = self._create_analysis_prompt(cv_text, job_description)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career advisor and CV analyst. "
                        "Analyze CVs against job descriptions and provide detailed, "
                        "actionable feedback in JSON format.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            return self._parse_analysis_result(result)

        except Exception as e:
            raise RuntimeError(f"AI analysis failed: {str(e)}")

    def _create_analysis_prompt(self, cv_text: str, job_description: str) -> str:
        """Create the prompt for AI analysis."""
        return f"""
Analyze the following CV against the job description and provide a comprehensive assessment.

JOB DESCRIPTION:
{job_description}

CV CONTENT:
{cv_text}

Provide a detailed analysis in JSON format with the following structure:
{{
    "match_score": {{
        "overall_score": <0-100>,
        "skills_match": <0-100>,
        "experience_match": <0-100>,
        "education_match": <0-100>,
        "keywords_match": <0-100>,
        "matching_skills": [list of skills that match],
        "missing_skills": [list of important skills missing from CV],
        "matching_keywords": [list of important keywords found],
        "missing_keywords": [list of important keywords missing]
    }},
    "formatting_advice": {{
        "strengths": [list of CV strengths],
        "weaknesses": [list of CV weaknesses],
        "suggestions": [list of specific improvement suggestions],
        "structure_feedback": "feedback on CV structure and layout",
        "content_feedback": "feedback on CV content quality"
    }},
    "summary": "overall summary of how well the CV matches the job",
    "recommendation": "clear recommendation for the candidate"
}}

Be thorough, specific, and constructive in your analysis.
"""

    def _parse_analysis_result(self, result: dict) -> CVAnalysis:
        """Parse AI response into CVAnalysis object."""
        try:
            match_score = MatchScore(**result["match_score"])
            formatting_advice = FormattingAdvice(**result["formatting_advice"])

            return CVAnalysis(
                match_score=match_score,
                formatting_advice=formatting_advice,
                summary=result["summary"],
                recommendation=result["recommendation"],
            )
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid AI response format: {str(e)}")
