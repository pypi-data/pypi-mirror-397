# Quick Start Guide

## 1. Launch the Web UI (Easiest Method)

### Installation
```bash
cd /Users/garubamalik/Documents/pypi_projects/cv-matcher
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Launch UI
```bash
python launch_ui.py
```

Then open your browser to `http://localhost:7860`

## 2. Using the Web Interface

1. **Upload CV**: Click "Upload CV (PDF)" and select your PDF resume
2. **Add Job Description**: Either:
   - Paste the job description in the text area, OR
   - Provide a URL to the job posting
3. **Click "Analyze CV"**: Wait for the analysis (first run takes longer as model downloads)
4. **View Results**: See your match score, skills analysis, and formatting advice

## 3. Using in Python Code

### With Local Model (No API Key)
```python
from cv_matcher import CVMatcher

matcher = CVMatcher(use_local_model=True)
analysis = matcher.analyze_cv("cv.pdf", "job description")
matcher.print_analysis(analysis)
```

### Launch UI Programmatically
```python
from cv_matcher import launch_ui

launch_ui(
    model_name="microsoft/Phi-3-mini-4k-instruct",
    share=False,  # Set True for public URL
    port=7860
)
```

## 4. Command Line Launch

```bash
# Basic launch
python -c "from cv_matcher import launch_ui; launch_ui()"

# With public sharing
python -c "from cv_matcher import launch_ui; launch_ui(share=True)"

# On different port
python -c "from cv_matcher import launch_ui; launch_ui(port=8080)"
```

## Notes

- **First Run**: Downloads ~3-7GB AI model (one-time, cached for future use)
- **Privacy**: All data stays on your machine with local models
- **No API Keys**: Completely free to use with local models
- **GPU**: Automatically uses GPU if available (CUDA), falls back to CPU

## Troubleshooting

### Model Download Issues
If model download fails, try:
```bash
export HF_HUB_ENABLE_HF_TRANSFER=1
```

### Memory Issues
If you run out of memory, use a smaller model:
```python
from cv_matcher import launch_ui
launch_ui(model_name="microsoft/Phi-3-mini-4k-instruct")  # Smallest option
```

### Port Already in Use
```python
launch_ui(port=8080)  # Use different port
```
