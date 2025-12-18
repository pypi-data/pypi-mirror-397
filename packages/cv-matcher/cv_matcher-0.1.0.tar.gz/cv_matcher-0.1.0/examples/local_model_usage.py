"""
Example: Using CV Matcher with local model (no API key required).
"""

from cv_matcher import CVMatcher


def main():
    # Initialize with local model (default)
    print("Initializing CV Matcher with local AI model...")
    matcher = CVMatcher(use_local_model=True)

    # Job description
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
    print("\nAnalyzing CV...")
    analysis = matcher.analyze_cv(
        cv_path="path/to/your/cv.pdf",  # Update with actual path
        job_description=job_description,
        verbose=True,
    )

    # Display results
    print("\n" + "=" * 80 + "\n")
    matcher.print_analysis(analysis, detailed=True)

    # Export to JSON
    matcher.export_analysis(analysis, "cv_analysis_result.json")


if __name__ == "__main__":
    main()
