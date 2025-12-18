"""
Local AI analyzer for matching CVs with job descriptions using Hugging Face models.
No API key required - runs completely locally.
"""

import json
from typing import Optional
from cv_matcher.models import CVAnalysis, MatchScore, FormattingAdvice

# Lazy imports for optional dependencies
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None


class LocalAIAnalyzer:
    """
    Analyze CVs and job descriptions using local LLM models.
    No API keys required - completely offline and free to use.
    """

    def __init__(
        self, model_name: str = "microsoft/Phi-3-mini-4k-instruct", device: Optional[str] = None
    ):
        """
        Initialize the local AI analyzer.

        Args:
            model_name: Hugging Face model to use. Default is Phi-3 (small, efficient)
                       Other options: "mistralai/Mistral-7B-Instruct-v0.2"
            device: Device to run model on ("cuda", "cpu", or None for auto-detect)
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Local model dependencies are not installed. Install them with:\n"
                "pip install cv-matcher[local]\n"
                "Or use OpenAI instead: CVMatcher(use_local_model=False)"
            )

        self.model_name = model_name

        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Lazy loading - only load when needed
        self.model = None
        self.tokenizer = None
        self.pipe = None

    def _ensure_model_loaded(self):
        """Load model if not already loaded (lazy loading)."""
        if self.model is not None:
            return  # Already loaded

        print(f"Loading model {self.model_name} on {self.device}...")

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)

        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True,
            attn_implementation="eager",  # Use eager attention (compatible with all models)
            use_cache=True,
        )

        if self.device == "cpu":
            self.model = self.model.to(self.device)

        # Create text generation pipeline without cache to avoid compatibility issues
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=2048,
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        # Configure generation to not use cache
        self.generation_config = {
            "use_cache": False,  # Disable cache to prevent DynamicCache errors
            "return_full_text": False,
            "clean_up_tokenization_spaces": True,
        }

        print("✓ Model loaded successfully!")

    def analyze(self, cv_text: str, job_description: str) -> CVAnalysis:
        """
        Analyze CV against job description.

        Args:
            cv_text: Extracted CV text
            job_description: Job description text

        Returns:
            CVAnalysis object with match score and formatting advice
        """
        # Load model if not already loaded
        self._ensure_model_loaded()

        prompt = self._create_analysis_prompt(cv_text, job_description)

        try:
            # Generate analysis with cache disabled to prevent errors
            outputs = self.pipe(
                prompt,
                **self.generation_config,
            )
            response = outputs[0]["generated_text"]

            # Extract JSON from response (remove the prompt)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in model response")

            json_str = response[json_start:json_end]
            result = json.loads(json_str)

            return self._parse_analysis_result(result)

        except Exception as e:
            # Fallback to basic analysis if model fails
            print(f"Warning: AI analysis failed ({str(e)}), using fallback analysis")
            return self._fallback_analysis(cv_text, job_description)

    def _create_analysis_prompt(self, cv_text: str, job_description: str) -> str:
        """Create the prompt for AI analysis."""
        return f"""<|system|>
You are an expert career advisor and CV analyst. Analyze CVs against job descriptions and provide detailed, actionable feedback in JSON format only.<|end|>
<|user|>
Analyze the following CV against the job description and provide a comprehensive assessment.

JOB DESCRIPTION:
{job_description[:1500]}

CV CONTENT:
{cv_text[:2000]}

Provide ONLY a valid JSON object (no other text) with this exact structure:
{{
    "match_score": {{
        "overall_score": 75,  // Must be weighted average: (skills_match * 0.35) + (experience_match * 0.30) + (education_match * 0.20) + (keywords_match * 0.15)
        "skills_match": 80,
        "experience_match": 70,
        "education_match": 65,
        "keywords_match": 85,
        "matching_skills": ["skill1", "skill2"],
        "missing_skills": ["skill3", "skill4"],
        "matching_keywords": ["keyword1", "keyword2"],
        "missing_keywords": ["keyword3"]
    }},
    "formatting_advice": {{
        "strengths": ["strength1", "strength2"],
        "weaknesses": ["weakness1", "weakness2"],
        "suggestions": ["suggestion1", "suggestion2"],
        "structure_feedback": "feedback on structure",
        "content_feedback": "feedback on content"
    }},
    "summary": "overall summary",
    "recommendation": "recommendation for candidate"
}}

JSON response:<|end|>
<|assistant|>
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

    def _fallback_analysis(self, cv_text: str, job_description: str) -> CVAnalysis:
        """
        Provide basic rule-based analysis when AI model fails.
        """
        cv_lower = cv_text.lower()
        job_lower = job_description.lower()

        # Extract common skills and keywords
        common_skills = [
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "ruby",
            "php",
            "go",
            "rust",
            "react",
            "angular",
            "vue",
            "django",
            "flask",
            "spring",
            "node",
            "express",
            "docker",
            "kubernetes",
            "jenkins",
            "ci/cd",
            "devops",
            "sql",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "nosql",
            "aws",
            "azure",
            "gcp",
            "cloud",
            "git",
            "github",
            "gitlab",
            "api",
            "rest",
            "graphql",
            "microservices",
            "agile",
            "scrum",
        ]

        experience_keywords = [
            "years experience",
            "year of experience",
            "senior",
            "lead",
            "manager",
            "developed",
            "built",
            "designed",
            "implemented",
            "managed",
            "led",
        ]

        education_keywords = [
            "bachelor",
            "master",
            "phd",
            "degree",
            "university",
            "college",
            "computer science",
            "engineering",
            "certification",
            "certified",
        ]

        # Find matching and missing skills
        matching_skills = [
            skill for skill in common_skills if skill in cv_lower and skill in job_lower
        ]
        missing_skills = [
            skill for skill in common_skills if skill in job_lower and skill not in cv_lower
        ]

        # Calculate skills match
        total_skills = len(matching_skills) + len(missing_skills)
        if total_skills > 0:
            skills_match = (len(matching_skills) / total_skills) * 100
        else:
            skills_match = 50.0  # Neutral score if no specific skills detected

        # Calculate experience match based on keyword presence
        exp_in_cv = sum(1 for kw in experience_keywords if kw in cv_lower)
        exp_in_job = sum(1 for kw in experience_keywords if kw in job_lower)
        if exp_in_job > 0:
            experience_match = min((exp_in_cv / exp_in_job) * 100, 100)
        else:
            experience_match = 50.0  # Neutral if can't determine

        # Add bonus if CV is longer (more detailed)
        if len(cv_text) > 1000:
            experience_match = min(experience_match + 10, 100)

        # Calculate education match
        edu_in_cv = sum(1 for kw in education_keywords if kw in cv_lower)
        edu_in_job = sum(1 for kw in education_keywords if kw in job_lower)
        if edu_in_job > 0:
            education_match = min((edu_in_cv / edu_in_job) * 100, 100)
        else:
            education_match = 60.0  # Neutral if education not emphasized

        # Calculate keywords match - how many job keywords appear in CV
        job_words = set(job_lower.split())
        cv_words = set(cv_lower.split())
        # Filter out common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "be",
            "been",
        }
        job_keywords = job_words - stop_words
        matching_keywords = job_keywords.intersection(cv_words)

        if len(job_keywords) > 0:
            keywords_match = (len(matching_keywords) / len(job_keywords)) * 100
        else:
            keywords_match = 50.0

        # Cap at reasonable max
        keywords_match = min(keywords_match, 85)

        # Calculate overall score as weighted average of component scores
        # Skills: 35%, Experience: 30%, Education: 20%, Keywords: 15%
        overall_score = (
            (skills_match * 0.35)
            + (experience_match * 0.30)
            + (education_match * 0.20)
            + (keywords_match * 0.15)
        )

        match_score = MatchScore(
            overall_score=round(overall_score, 1),
            skills_match=round(skills_match, 1),
            experience_match=round(experience_match, 1),
            education_match=round(education_match, 1),
            keywords_match=round(keywords_match, 1),
            matching_skills=matching_skills if matching_skills else ["No specific skills detected"],
            missing_skills=(
                missing_skills if missing_skills else ["Upload detailed CV for better analysis"]
            ),
            matching_keywords=list(matching_keywords)[:10] if matching_keywords else [],
            missing_keywords=list(job_keywords - matching_keywords)[:10] if job_keywords else [],
        )

        # Generate contextual advice based on scores
        strengths = []
        weaknesses = []
        suggestions = []

        if skills_match >= 60:
            strengths.append("Good technical skills alignment with job requirements")
        elif skills_match < 40:
            weaknesses.append("Limited matching technical skills found")
            suggestions.append("Add relevant technical skills from the job description to your CV")

        if experience_match >= 60:
            strengths.append("Experience level appears appropriate for the role")
        else:
            weaknesses.append("Experience indicators could be stronger")
            suggestions.append("Use action verbs and quantify your achievements")

        if keywords_match >= 60:
            strengths.append("Good use of industry-relevant keywords")
        else:
            suggestions.append("Incorporate more keywords from the job description naturally")

        if not strengths:
            strengths.append("CV content extracted successfully")
        if not weaknesses:
            weaknesses.append("Consider tailoring CV more specifically to this role")
        if not suggestions:
            suggestions.append("Review job description and highlight relevant experience")

        formatting_advice = FormattingAdvice(
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            structure_feedback="Basic keyword analysis performed. For more accurate results, the AI model needs to be loaded.",
            content_feedback="Consider using a more detailed CV with specific achievements and quantifiable results.",
        )

        return CVAnalysis(
            match_score=match_score,
            formatting_advice=formatting_advice,
            summary="Basic keyword-based analysis performed. CV shows partial match with job requirements.",
            recommendation="Review missing skills and consider highlighting relevant experience more prominently.",
        )
