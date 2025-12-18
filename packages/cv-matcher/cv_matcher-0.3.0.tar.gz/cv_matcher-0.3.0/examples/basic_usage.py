"""
Basic usage example for CV Matcher library.
"""

import os
from cv_matcher import CVMatcher


def main():
    # Set your OpenAI API key
    # Option 1: Via environment variable (recommended)
    # export OPENAI_API_KEY="your-api-key"

    # Option 2: Pass directly (not recommended for production)
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    # Initialize the CV matcher
    matcher = CVMatcher(api_key=api_key)

    # Job description (can be text or URL)
    job_description = """
    Senior Python Developer
    
    We are looking for an experienced Python developer to join our team.
    
    Requirements:
    - 5+ years of Python development experience
    - Strong knowledge of Django or Flask
    - Experience with REST APIs
    - Understanding of SQL and NoSQL databases
    - Experience with Docker and Kubernetes
    - Good communication skills
    
    Responsibilities:
    - Design and develop scalable backend systems
    - Write clean, maintainable code
    - Collaborate with frontend developers
    - Participate in code reviews
    """

    # Analyze CV
    print("Analyzing CV...")
    analysis = matcher.analyze_cv(
        cv_path="path/to/your/cv.pdf",  # Update with actual path
        job_description=job_description,
        verbose=True,  # Show progress
    )

    # Display results
    print("\n" + "=" * 80 + "\n")
    matcher.print_analysis(analysis, detailed=True)

    # Export to JSON
    matcher.export_analysis(analysis, "cv_analysis_result.json")

    # Access specific scores programmatically
    print(f"\n\nOverall Match Score: {analysis.match_score.overall_score:.1f}%")
    print(f"Skills Match: {analysis.match_score.skills_match:.1f}%")

    if analysis.match_score.missing_skills:
        print(f"\nTop 5 Missing Skills:")
        for skill in analysis.match_score.missing_skills[:5]:
            print(f"  - {skill}")


if __name__ == "__main__":
    main()
