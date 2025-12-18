"""
Shared test fixtures and configuration.
"""

import pytest


@pytest.fixture
def sample_cv_text():
    """Sample CV text for testing."""
    return """
    John Doe
    Software Engineer
    
    Experience:
    - Senior Python Developer at TechCorp (2020-2023)
    - Junior Developer at StartupXYZ (2018-2020)
    
    Skills:
    - Python, Django, Flask
    - JavaScript, React
    - SQL, PostgreSQL
    - Docker, Kubernetes
    - Git, CI/CD
    
    Education:
    - B.S. Computer Science, University of Technology (2018)
    """


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    Senior Python Developer
    
    We are seeking an experienced Python developer.
    
    Requirements:
    - 5+ years Python experience
    - Django or Flask framework
    - REST API development
    - Docker and Kubernetes
    - Strong SQL skills
    
    Responsibilities:
    - Build scalable backend systems
    - Write clean code
    - Mentor junior developers
    """


@pytest.fixture
def mock_api_key():
    """Mock OpenAI API key for testing."""
    return "test-api-key-12345"
