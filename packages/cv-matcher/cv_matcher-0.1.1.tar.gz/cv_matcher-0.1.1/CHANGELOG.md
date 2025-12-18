# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-12-16

### Changed
- **BREAKING**: Default behavior now uses OpenAI API instead of local models for better performance
- Moved `transformers`, `torch`, and `accelerate` to optional `[local]` dependencies
- Moved `openai` from optional to core dependencies
- Updated README and documentation to reflect OpenAI as primary option
- UI now defaults to OpenAI, with local models as an option (`use_local_model=True`)

### Added
- `use_local_model` parameter to UI initialization and launch_ui function
- `PUBLISH.md` comprehensive guide for PyPI publishing workflow
- `.pypirc` template for Test PyPI and PyPI configuration
- Enhanced changelog documentation

### Fixed
- Improved fallback analysis to calculate all scores based on actual content analysis
- Fixed inconsistent scoring when skills match is 0% but other scores showed 60%+
- Fixed DynamicCache 'seen_tokens' attribute errors with local models
- All fallback scores now use rule-based analysis instead of hardcoded values

### Performance
- Significantly faster analysis with OpenAI GPT-4 (default)
- More accurate scoring and recommendations with cloud-based models

## [0.2.0] - 2025-12-15

### Added
- Local AI model support using Hugging Face Transformers (Phi-3, Mistral, etc.)
- Gradio web UI for user-friendly, no-code CV analysis
- Lazy loading for models to improve import speed
- Detailed feedback sections in UI with score explanations
- Score breakdowns with visual progress bars and tips
- Enhanced skills analysis with matching/missing categorization
- Optional OpenAI dependency (moved from core)

### Fixed
- Import errors when OpenAI not installed (made it optional)
- Model loading performance issues at import time
- UI readability issues (purple text on pink background)
- Overall score calculation now uses weighted average formula
- Terminal color output compatibility

## [0.1.0] - 2025-12-15

### Added
- Initial release of CV Matcher library
- PDF CV parsing functionality
- Job description fetching from text or URLs
- AI-powered CV analysis using OpenAI GPT models
- Match scoring system (overall, skills, experience, education, keywords)
- Formatting advice and suggestions
- Rich CLI output with colors and tables
- Export analysis results to JSON
- Comprehensive documentation and examples
- Test suite with pytest
- GitHub Actions CI/CD workflows
- Support for Python 3.9+

### Features
- `CVMatcher` main class for easy usage
- `PDFParser` for extracting text from PDF files
- `JobDescriptionFetcher` for fetching job descriptions
- `AIAnalyzer` for AI-powered analysis
- Pydantic models for type safety
- Beautiful terminal output with Rich library

[Unreleased]: https://github.com/yourusername/cv-matcher/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/cv-matcher/releases/tag/v0.1.0
