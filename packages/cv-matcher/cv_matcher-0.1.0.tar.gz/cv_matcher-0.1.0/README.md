# CV Matcher 🎯

An AI-powered Python library for analyzing CVs (resumes) against job descriptions. Get match scores, identify missing skills, and receive expert formatting advice to improve your CV.

**✨ Features Web UI with OpenAI GPT-4 for Best Performance ✨**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features ✨

- 🌐 **Web UI**: Beautiful Gradio-based interface - no coding required!
- 🤖 **AI-Powered Analysis**: OpenAI GPT-4 for intelligent, accurate analysis
- 🔓 **Local Models Option**: Use local AI models (Phi-3, Mistral, etc.) - no API keys required
- 📄 **PDF CV Parsing**: Extract text from PDF CVs with ease
- 🔍 **Job Description Fetching**: Accept job descriptions as text or fetch from URLs
- 📊 **Detailed Match Scoring**: Get scores for skills, experience, education, and keywords
- 💡 **Formatting Advice**: Receive actionable suggestions to improve your CV
- 🎨 **Beautiful Output**: Rich, colorful terminal and web UI
- 📤 **Export Results**: Save analysis results to JSON for further processing

## Installation 📦

### Using pip

```bash
pip install cv-matcher

# Create a .env file for configuration
cp .env.example .env

# Edit .env and set your preferences:
# - USE_LOCAL_MODEL=false (use OpenAI, recommended)
# - USE_LOCAL_MODEL=true (use local models, no API key needed)
# - OPENAI_API_KEY=your-key-here (required if USE_LOCAL_MODEL=false)
```

### For Local Models Only

```bash
# Install with local model dependencies
pip install cv-matcher[local]

# Set USE_LOCAL_MODEL=true in .env
echo "USE_LOCAL_MODEL=true" > .env
```

### Using uv (recommended for development)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/cv-matcher.git
cd cv-matcher

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

## Configuration ⚙️

### Environment Variables (.env file)

Create a `.env` file in your project root to configure the AI backend:

```bash
# Toggle between local and OpenAI models
USE_LOCAL_MODEL=false  # false=OpenAI (default), true=local models

# OpenAI Configuration (required if USE_LOCAL_MODEL=false)
OPENAI_API_KEY=your-openai-api-key-here
# OPENAI_MODEL=gpt-4o-mini  # Optional, defaults to gpt-4o-mini

# Local Model Configuration (used if USE_LOCAL_MODEL=true)
# LOCAL_MODEL_NAME=microsoft/Phi-3-mini-4k-instruct  # Optional
```

**Switching Models:**
- Set `USE_LOCAL_MODEL=false` to use OpenAI (faster, more accurate, requires API key)
- Set `USE_LOCAL_MODEL=true` to use local models (private, no API key, slower)

The launcher script automatically reads these settings - no code changes needed!

## Quick Start 🚀

### Option 1: Web UI (Easiest! 🌐)

```python
from cv_matcher import launch_ui

# Launch the web interface
# Uses settings from .env file (USE_LOCAL_MODEL and OPENAI_API_KEY)
launch_ui()
```

Or launch from command line:
```bash
python launch_ui.py  # Reads USE_LOCAL_MODEL from .env
```

Then open your browser to `http://localhost:7860` and start analyzing CVs!

**💡 Tip:** Toggle between OpenAI and local models by changing `USE_LOCAL_MODEL` in your `.env` file - no code changes needed!

### Option 2: Python API with OpenAI (Recommended! ⚡)

```python
import os
from cv_matcher import CVMatcher

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Initialize with OpenAI (default for best performance)
matcher = CVMatcher(use_local_model=False)

# Analyze a CV against a job description
analysis = matcher.analyze_cv(
    cv_path="path/to/cv.pdf",
    job_description="Job description text or URL here",
    verbose=True
)

# Print the results
matcher.print_analysis(analysis)

# Export to JSON
matcher.export_analysis(analysis, "analysis_results.json")
```

### Option 3: Use Local Models (No API Key Required 🔓)

```python
from cv_matcher import CVMatcher

# Use local AI model (no API key needed, but slower)
matcher = CVMatcher(
    use_local_model=True,
    local_model_name="microsoft/Phi-3-mini-4k-instruct"  # Optional, this is default
)
    api_key="your-openai-api-key"
)

analysis = matcher.analyze_cv("cv.pdf", "job description")
```

### Launch Web UI from Command Line

```bash
# Simple way
python launch_ui.py

# Or with Python
python -c "from cv_matcher import launch_ui; launch_ui()"

# Create a public URL to share
python -c "from cv_matcher import launch_ui; launch_ui(share=True)"
```

### Job Description from URL

```python
matcher = CVMatcher()

# Fetch job description from a URL
analysis = matcher.analyze_cv(
    cv_path="cv.pdf",
    job_description="https://example.com/job-posting"
)
```

## API Configuration 🔧

### CVMatcher Parameters

```python
CVMatcher(
    use_local_model: bool = False,    # False=OpenAI (default), True=local models
    local_model_name: str = "microsoft/Phi-3-mini-4k-instruct",
    api_key: Optional[str] = None,    # OpenAI key (reads from .env if not provided)
    model: str = "gpt-4o-mini",       # OpenAI model name
    timeout: int = 10                 # HTTP timeout in seconds
)
```

**Recommended:** Use `.env` file for configuration instead of hardcoding parameters.

### Supported Local Models (No API Key Required)

- `microsoft/Phi-3-mini-4k-instruct` (default, fast, 3.8B parameters)
- `mistralai/Mistral-7B-Instruct-v0.2` (larger, more capable)
- Any Hugging Face instruction-tuned chat model

### Supported OpenAI Models (Requires API Key)

- `gpt-4o-mini` (cost-effective)
- `gpt-4o` (more advanced)
- `gpt-4-turbo` (high performance)

## Output Format 📋

The analysis returns a `CVAnalysis` object containing:

### Match Score
- **Overall Score**: 0-100% match rating
- **Skills Match**: How well skills align
- **Experience Match**: Experience level alignment
- **Education Match**: Education requirements match
- **Keywords Match**: Important keywords coverage
- **Matching/Missing Skills**: Lists of skills found and needed
- **Matching/Missing Keywords**: Key terms analysis

### Formatting Advice
- **Strengths**: What your CV does well
- **Weaknesses**: Areas needing improvement
- **Suggestions**: Specific, actionable recommendations
- **Structure Feedback**: Layout and organization advice
- **Content Feedback**: Content quality assessment

### Summary & Recommendation
- Overall assessment of the CV-job fit
- Clear recommendation for next steps

## Examples 📚

Check out the [examples](examples/) directory for more detailed usage examples:

- `local_model_usage.py`: Using local AI models (no API key)
- `basic_usage.py`: Simple CV analysis (works with both local and OpenAI)
- `batch_analysis.py`: Analyze multiple CVs
- `url_fetching.py`: Fetch job descriptions from URLs
- `custom_model.py`: Use different AI models
- `launch_ui.py`: Launch the web interface

## Development 🛠️

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/cv-matcher.git
cd cv-matcher

# Install with development dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v --cov=cv_matcher
```

### Code Formatting

```bash
# Format code
black src/cv_matcher

# Lint code
ruff check src/cv_matcher

# Type checking
mypy src/cv_matcher
```

## Project Structure 📁

```
cv-matcher/
├── src/
│   └── cv_matcher/
│       ├── __init__.py          # Package initialization
│       ├── matcher.py           # Main CVMatcher class
│       ├── models.py            # Pydantic data models
│       ├── pdf_parser.py        # PDF text extraction
│       ├── job_fetcher.py       # Job description fetching
│       └── ai_analyzer.py       # AI analysis logic
├── tests/                       # Test files
├── examples/                    # Usage examples
├── pyproject.toml              # Project configuration
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## Requirements 📋

- Python 3.9+
- **No API keys required** (when using local models)
- Dependencies (automatically installed):
  - pypdf
  - requests
  - beautifulsoup4
  - transformers
  - torch
  - gradio
  - pydantic
  - rich
  - accelerate
  
**Note:** First run will download the AI model (~3-7GB depending on model choice). Subsequent runs use cached model.

## API Reference 📖

### CVMatcher

Main class for CV analysis.

#### Methods

- `analyze_cv(cv_path, job_description, verbose=False)`: Analyze a CV
- `print_analysis(analysis, detailed=True)`: Display results
- `export_analysis(analysis, output_path)`: Save to JSON

### Models

- `CVAnalysis`: Complete analysis result
- `MatchScore`: Match scoring details
- `FormattingAdvice`: CV improvement suggestions

## Privacy & Security 🔒

### With Local Models (Default) 🔐
- **100% Private**: All data stays on your machine
- **No internet required**: Model runs completely offline after initial download
- **No API keys**: No external services involved
- **Your data never leaves your computer**

### With OpenAI (Optional)
- Your CV and job description data are sent to OpenAI for analysis
- No data is stored by this library
- Use environment variables for API keys (never hardcode them)
- Consider using `.env` files (excluded from git) for local development

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap 🗺️

- [x] Web UI with Gradio
- [x] Local AI models (no API key required)
- [ ] Support for more file formats (DOCX, TXT)
- [ ] Mobile-responsive UI
- [ ] Custom AI prompts for specific industries
- [ ] Integration with job board APIs
- [ ] Resume builder based on job description
- [ ] Batch processing UI
- [ ] Multi-language support
- [ ] Docker container for easy deployment

## Support 💬

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/cv-matcher/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/cv-matcher/discussions)

## Acknowledgments 🙏

- OpenAI for providing the GPT API
- The Python community for excellent libraries
- All contributors and users of this library

---

Made with ❤️ by the CV Matcher team
