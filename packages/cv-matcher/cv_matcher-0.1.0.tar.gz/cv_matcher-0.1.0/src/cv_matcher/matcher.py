"""
Main CVMatcher class - the primary interface for the library.
"""

from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from cv_matcher.pdf_parser import PDFParser
from cv_matcher.job_fetcher import JobDescriptionFetcher
from cv_matcher.ai_analyzer import AIAnalyzer
from cv_matcher.local_analyzer import LocalAIAnalyzer
from cv_matcher.models import CVAnalysis


class CVMatcher:
    """
    Main class for CV analysis and job matching.

    This class provides a simple interface to analyze CVs against job descriptions,
    calculate match scores, and provide formatting advice.

    Example:
        >>> matcher = CVMatcher(api_key="your-openai-key")
        >>> analysis = matcher.analyze_cv("cv.pdf", "Software Engineer at TechCorp...")
        >>> print(f"Match Score: {analysis.match_score.overall_score}%")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        timeout: int = 10,
        use_local_model: bool = True,
        local_model_name: str = "microsoft/Phi-3-mini-4k-instruct",
    ):
        """
        Initialize the CVMatcher.

        Args:
            api_key: OpenAI API key (only needed if use_local_model=False)
            model: OpenAI model to use for analysis (only if use_local_model=False)
            timeout: Timeout for HTTP requests when fetching job descriptions
            use_local_model: If True, uses local LLM (no API key needed). Default: True
            local_model_name: Hugging Face model to use locally
        """
        self.pdf_parser = PDFParser()
        self.job_fetcher = JobDescriptionFetcher(timeout=timeout)
        self.use_local_model = use_local_model

        if use_local_model:
            self.ai_analyzer = LocalAIAnalyzer(model_name=local_model_name)
        else:
            self.ai_analyzer = AIAnalyzer(api_key=api_key, model=model)

        self.console = Console()

    def analyze_cv(self, cv_path: str, job_description: str, verbose: bool = False) -> CVAnalysis:
        """
        Analyze a CV against a job description.

        Args:
            cv_path: Path to the CV PDF file
            job_description: Job description text or URL
            verbose: If True, print detailed progress information

        Returns:
            CVAnalysis object containing match score and formatting advice

        Raises:
            FileNotFoundError: If CV file doesn't exist
            ValueError: If CV or job description cannot be processed
            RuntimeError: If AI analysis fails
        """
        if verbose:
            self.console.print("[bold blue]Starting CV analysis...[/bold blue]")

        # Extract CV text
        if verbose:
            self.console.print("📄 Extracting text from CV PDF...")
        cv_text = self.pdf_parser.extract_text(cv_path)

        if verbose:
            self.console.print(f"✓ Extracted {len(cv_text)} characters from CV")

        # Fetch job description
        if verbose:
            self.console.print("🔍 Processing job description...")
        job_desc = self.job_fetcher.fetch(job_description)

        if verbose:
            self.console.print(f"✓ Processed {len(job_desc)} characters of job description")

        # Analyze with AI
        if verbose:
            self.console.print("🤖 Analyzing CV with AI...")
        analysis = self.ai_analyzer.analyze(cv_text, job_desc)

        if verbose:
            self.console.print("[bold green]✓ Analysis complete![/bold green]\n")

        return analysis

    def print_analysis(self, analysis: CVAnalysis, detailed: bool = True) -> None:
        """
        Print analysis results in a formatted way.

        Args:
            analysis: CVAnalysis object to print
            detailed: If True, print detailed information; otherwise, print summary
        """
        # Overall Score
        score = analysis.match_score.overall_score
        score_color = self._get_score_color(score)

        self.console.print(
            Panel(
                f"[bold {score_color}]{score:.1f}%[/bold {score_color}]",
                title="[bold]Overall Match Score[/bold]",
                expand=False,
            )
        )

        if detailed:
            # Detailed Scores Table
            table = Table(title="Detailed Scores", show_header=True, header_style="bold")
            table.add_column("Category", style="cyan")
            table.add_column("Score", justify="right")

            scores = [
                ("Skills Match", analysis.match_score.skills_match),
                ("Experience Match", analysis.match_score.experience_match),
                ("Education Match", analysis.match_score.education_match),
                ("Keywords Match", analysis.match_score.keywords_match),
            ]

            for category, score_val in scores:
                color = self._get_score_color(score_val)
                table.add_row(category, f"[{color}]{score_val:.1f}%[/{color}]")

            self.console.print(table)
            self.console.print()

            # Matching Skills
            if analysis.match_score.matching_skills:
                self.console.print("[bold green]✓ Matching Skills:[/bold green]")
                for skill in analysis.match_score.matching_skills[:10]:
                    self.console.print(f"  • {skill}")
                self.console.print()

            # Missing Skills
            if analysis.match_score.missing_skills:
                self.console.print("[bold yellow]⚠ Missing Skills:[/bold yellow]")
                for skill in analysis.match_score.missing_skills[:10]:
                    self.console.print(f"  • {skill}")
                self.console.print()

            # Formatting Advice
            self.console.print("[bold]📝 Formatting Advice:[/bold]")

            if analysis.formatting_advice.strengths:
                self.console.print("\n[green]Strengths:[/green]")
                for strength in analysis.formatting_advice.strengths:
                    self.console.print(f"  ✓ {strength}")

            if analysis.formatting_advice.weaknesses:
                self.console.print("\n[yellow]Areas for Improvement:[/yellow]")
                for weakness in analysis.formatting_advice.weaknesses:
                    self.console.print(f"  ⚠ {weakness}")

            if analysis.formatting_advice.suggestions:
                self.console.print("\n[cyan]Suggestions:[/cyan]")
                for suggestion in analysis.formatting_advice.suggestions:
                    self.console.print(f"  → {suggestion}")

            self.console.print()

        # Summary and Recommendation
        self.console.print(
            Panel(analysis.summary, title="[bold]Summary[/bold]", border_style="blue")
        )

        self.console.print(
            Panel(
                analysis.recommendation, title="[bold]Recommendation[/bold]", border_style="green"
            )
        )

    def _get_score_color(self, score: float) -> str:
        """Get color for score display based on value."""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "yellow"
        elif score >= 40:
            return "orange"
        else:
            return "red"

    def export_analysis(self, analysis: CVAnalysis, output_path: str) -> None:
        """
        Export analysis to a JSON file.

        Args:
            analysis: CVAnalysis object to export
            output_path: Path to save the JSON file
        """
        import json

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w", encoding="utf-8") as f:
            json.dump(analysis.model_dump(), f, indent=2)

        self.console.print(f"[green]✓ Analysis exported to {output_path}[/green]")
