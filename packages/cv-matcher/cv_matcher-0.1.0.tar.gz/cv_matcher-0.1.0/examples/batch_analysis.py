"""
Example of batch processing multiple CVs.
"""

import os
from pathlib import Path
from cv_matcher import CVMatcher
import json


def batch_analyze_cvs():
    """Analyze multiple CVs against a single job description."""
    api_key = os.getenv("OPENAI_API_KEY")
    matcher = CVMatcher(api_key=api_key)

    # Job description
    job_description = """
    Software Engineer - Full Stack
    
    We're seeking a talented full-stack developer.
    
    Required Skills:
    - React and Node.js
    - Python or Java
    - SQL databases
    - RESTful APIs
    - Git version control
    """

    # Directory containing CVs
    cv_directory = Path("path/to/cv/folder")
    cv_files = list(cv_directory.glob("*.pdf"))

    print(f"Found {len(cv_files)} CVs to analyze\n")

    results = []

    for cv_path in cv_files:
        print(f"\n{'='*80}")
        print(f"Analyzing: {cv_path.name}")
        print("=" * 80)

        try:
            analysis = matcher.analyze_cv(
                cv_path=str(cv_path), job_description=job_description, verbose=False
            )

            # Store results
            results.append(
                {
                    "filename": cv_path.name,
                    "overall_score": analysis.match_score.overall_score,
                    "skills_match": analysis.match_score.skills_match,
                    "summary": analysis.summary,
                }
            )

            # Print summary
            print(f"Overall Score: {analysis.match_score.overall_score:.1f}%")
            print(f"Skills Match: {analysis.match_score.skills_match:.1f}%")

            # Export individual results
            output_name = f"analysis_{cv_path.stem}.json"
            matcher.export_analysis(analysis, output_name)

        except Exception as e:
            print(f"Error analyzing {cv_path.name}: {e}")
            results.append({"filename": cv_path.name, "error": str(e)})

    # Sort by overall score
    valid_results = [r for r in results if "overall_score" in r]
    valid_results.sort(key=lambda x: x["overall_score"], reverse=True)

    # Print ranking
    print(f"\n\n{'='*80}")
    print("RANKING OF CANDIDATES")
    print("=" * 80)

    for i, result in enumerate(valid_results, 1):
        print(f"{i}. {result['filename']}: {result['overall_score']:.1f}%")

    # Export summary
    with open("batch_analysis_summary.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✓ Batch analysis complete! Summary saved to batch_analysis_summary.json")


if __name__ == "__main__":
    batch_analyze_cvs()
