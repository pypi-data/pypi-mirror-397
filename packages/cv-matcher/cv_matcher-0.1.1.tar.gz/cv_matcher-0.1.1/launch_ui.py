"""
Launch the CV Matcher Web UI.
"""

import os
from dotenv import load_dotenv
from cv_matcher import launch_ui

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Read configuration from environment variables
    use_local_model = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    local_model_name = os.getenv("LOCAL_MODEL_NAME", "microsoft/Phi-3-mini-4k-instruct")

    # Launch the web interface
    # Toggle between OpenAI and local models using USE_LOCAL_MODEL in .env
    launch_ui(
        use_local_model=use_local_model,
        model_name=local_model_name,
        share=False,  # Set to True for public URL
        port=7860,
    )
