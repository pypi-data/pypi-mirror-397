"""
Example of fetching job descriptions from URLs.
"""

import os
from cv_matcher import CVMatcher


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    matcher = CVMatcher(api_key=api_key)

    # Example job posting URLs (replace with real URLs)
    job_urls = [
        "https://example.com/jobs/python-developer",
        "https://example.com/jobs/data-scientist",
    ]

    cv_path = "path/to/your/cv.pdf"  # Update with actual path

    for url in job_urls:
        print(f"\n{'='*80}")
        print(f"Analyzing CV against job posting: {url}")
        print("=" * 80)

        try:
            analysis = matcher.analyze_cv(
                cv_path=cv_path, job_description=url, verbose=True  # Pass URL directly
            )

            # Print summary
            matcher.print_analysis(analysis, detailed=False)

            # Export results
            filename = f"analysis_{url.split('/')[-1]}.json"
            matcher.export_analysis(analysis, filename)

        except Exception as e:
            print(f"Error analyzing job posting: {e}")


if __name__ == "__main__":
    main()
