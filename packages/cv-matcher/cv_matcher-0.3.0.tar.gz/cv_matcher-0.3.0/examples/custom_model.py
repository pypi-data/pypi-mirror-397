"""
Example of using different OpenAI models.
"""

import os
from cv_matcher import CVMatcher


def compare_models():
    """Compare results from different models."""
    api_key = os.getenv("OPENAI_API_KEY")

    cv_path = "path/to/your/cv.pdf"
    job_description = """
    Machine Learning Engineer
    
    Requirements:
    - PhD in Computer Science or related field
    - Strong background in ML/AI
    - Experience with PyTorch or TensorFlow
    - Publications in top-tier conferences
    """

    models = ["gpt-4o-mini", "gpt-4o"]

    for model in models:
        print(f"\n{'='*80}")
        print(f"Testing with model: {model}")
        print("=" * 80)

        try:
            matcher = CVMatcher(api_key=api_key, model=model)

            analysis = matcher.analyze_cv(
                cv_path=cv_path, job_description=job_description, verbose=False
            )

            print(f"\nModel: {model}")
            print(f"Overall Score: {analysis.match_score.overall_score:.1f}%")
            print(f"Summary: {analysis.summary[:200]}...")

        except Exception as e:
            print(f"Error with model {model}: {e}")


def use_custom_model():
    """Use a specific model configuration."""
    api_key = os.getenv("OPENAI_API_KEY")

    # Use GPT-4 for more detailed analysis
    matcher = CVMatcher(
        api_key=api_key,
        model="gpt-4o",  # More advanced model
        timeout=30,  # Longer timeout for detailed analysis
    )

    cv_path = "path/to/your/cv.pdf"
    job_description = "Your job description here..."

    analysis = matcher.analyze_cv(cv_path, job_description, verbose=True)
    matcher.print_analysis(analysis)


if __name__ == "__main__":
    print("Comparing models...")
    compare_models()

    print("\n\nUsing custom model configuration...")
    use_custom_model()
