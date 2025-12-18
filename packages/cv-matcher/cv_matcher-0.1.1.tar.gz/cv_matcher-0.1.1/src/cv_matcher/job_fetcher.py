"""
Job description fetcher for retrieving job postings from URLs or text.
"""

import requests
from bs4 import BeautifulSoup
import re


class JobDescriptionFetcher:
    """Fetch and process job descriptions from various sources."""

    def __init__(self, timeout: int = 10):
        """
        Initialize the job description fetcher.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def fetch(self, source: str) -> str:
        """
        Fetch job description from URL or return text directly.

        Args:
            source: Either a URL or plain text job description

        Returns:
            Job description text

        Raises:
            ValueError: If URL cannot be fetched or is invalid
        """
        # Check if source is a URL
        if self._is_url(source):
            return self._fetch_from_url(source)
        else:
            # Treat as plain text
            return source.strip()

    def _is_url(self, text: str) -> bool:
        """Check if text is a valid URL."""
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return bool(url_pattern.match(text.strip()))

    def _fetch_from_url(self, url: str) -> str:
        """
        Fetch job description from a URL.

        Args:
            url: URL to fetch from

        Returns:
            Extracted text content

        Raises:
            ValueError: If URL cannot be fetched
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text(separator="\n")

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = "\n".join(chunk for chunk in chunks if chunk)

            if not text.strip():
                raise ValueError("No text content found at URL")

            return text

        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing URL content: {str(e)}")

    def extract_key_info(self, job_description: str) -> dict:
        """
        Extract key information from job description.

        Args:
            job_description: Job description text

        Returns:
            Dictionary with extracted information
        """
        text_lower = job_description.lower()

        # Common section headers
        requirements_keywords = ["requirements", "qualifications", "required skills"]
        responsibilities_keywords = ["responsibilities", "duties", "what you will do"]

        info = {
            "has_requirements": any(keyword in text_lower for keyword in requirements_keywords),
            "has_responsibilities": any(
                keyword in text_lower for keyword in responsibilities_keywords
            ),
            "length": len(job_description),
            "word_count": len(job_description.split()),
        }

        return info
