"""
Gradio web UI for CV Matcher.
Launch a web interface for analyzing CVs against job descriptions.
"""

import gradio as gr
import json
from cv_matcher import CVMatcher
from cv_matcher.models import CVAnalysis


class CVMatcherUI:
    """Web UI for CV Matcher using Gradio."""

    def __init__(
        self, use_local_model: bool = False, model_name: str = "microsoft/Phi-3-mini-4k-instruct"
    ):
        """
        Initialize the CV Matcher UI.

        Args:
            use_local_model: Whether to use local models (True) or OpenAI (False)
            model_name: Hugging Face model to use for analysis if use_local_model=True
        """
        if use_local_model:
            print("Initializing CV Matcher with local model...")
            self.matcher = CVMatcher(use_local_model=True, local_model_name=model_name)
        else:
            print("Initializing CV Matcher with OpenAI...")
            self.matcher = CVMatcher(use_local_model=False)
        print("✓ CV Matcher ready!")

    def analyze_cv_ui(self, cv_file, job_description: str, job_url: str = ""):
        """
        Analyze CV from UI inputs.

        Args:
            cv_file: Uploaded PDF file
            job_description: Job description text
            job_url: Optional job URL to fetch description from

        Returns:
            Formatted analysis results
        """
        try:
            # Validate inputs
            if cv_file is None:
                return "❌ Please upload a CV PDF file.", "", "", "", ""

            if not job_description.strip() and not job_url.strip():
                return "❌ Please provide either a job description or a job URL.", "", "", "", ""

            # Use URL if provided, otherwise use text
            job_input = job_url if job_url.strip() else job_description

            # Analyze CV
            analysis = self.matcher.analyze_cv(
                cv_path=cv_file.name, job_description=job_input, verbose=False
            )

            # Format results
            summary_html = self._format_summary(analysis)
            scores_html = self._format_scores(analysis)
            skills_html = self._format_skills(analysis)
            advice_html = self._format_advice(analysis)
            json_output = json.dumps(analysis.model_dump(), indent=2)

            return summary_html, scores_html, skills_html, advice_html, json_output

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            return error_msg, "", "", "", ""

    def _format_summary(self, analysis: CVAnalysis) -> str:
        """Format summary section."""
        score = analysis.match_score.overall_score
        color = self._get_score_color(score)

        html = f"""
        <div style="padding: 20px; background: linear-gradient(135deg, {color}22 0%, {color}11 100%); 
                    border-left: 5px solid {color}; border-radius: 10px; margin: 10px 0;">
            <h2 style="color: {color}; margin: 0;">Overall Match Score: {score:.1f}%</h2>
            <p style="font-size: 18px; margin-top: 15px;"><strong>Summary:</strong></p>
            <p style="font-size: 16px; line-height: 1.6;">{analysis.summary}</p>
            <p style="font-size: 18px; margin-top: 15px;"><strong>Recommendation:</strong></p>
            <p style="font-size: 16px; line-height: 1.6; color: #2c5282;">{analysis.recommendation}</p>
        </div>
        """
        return html

    def _format_scores(self, analysis: CVAnalysis) -> str:
        """Format detailed scores section."""
        scores_data = [
            (
                "Skills Match",
                analysis.match_score.skills_match,
                "Measures how well your technical and professional skills align with the job requirements.",
                "Highlight relevant skills prominently in your CV.",
            ),
            (
                "Experience Match",
                analysis.match_score.experience_match,
                "Evaluates whether your work experience level and background match the position requirements.",
                "Emphasize relevant projects and achievements from similar roles.",
            ),
            (
                "Education Match",
                analysis.match_score.education_match,
                "Assesses if your educational background meets the job's qualification requirements.",
                "Include relevant certifications, courses, or training that complement your degree.",
            ),
            (
                "Keywords Match",
                analysis.match_score.keywords_match,
                "Checks for important keywords and industry-specific terms from the job description.",
                "Incorporate job-specific terminology naturally throughout your CV.",
            ),
        ]

        html = "<div style='padding: 15px;'>"
        html += "<h3>Detailed Score Breakdown</h3>"
        html += "<p style='color: #666; margin-bottom: 20px;'>Each score reflects a different aspect of your CV's alignment with the job requirements.</p>"

        for category, score, description, tip in scores_data:
            color = self._get_score_color(score)
            percentage = score

            # Score interpretation
            if percentage >= 80:
                interpretation = "Excellent match! 🎉"
                interp_color = "#38a169"
            elif percentage >= 60:
                interpretation = "Good match 👍"
                interp_color = "#d69e2e"
            elif percentage >= 40:
                interpretation = "Moderate match 📈"
                interp_color = "#dd6b20"
            else:
                interpretation = "Needs improvement 💪"
                interp_color = "#e53e3e"

            html += f"""
            <div style="margin: 25px 0; padding: 15px; background: #f7fafc; border-radius: 8px; border-left: 4px solid {color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: bold; font-size: 16px;">{category}</span>
                    <span style="color: {color}; font-weight: bold; font-size: 18px;">{percentage:.1f}%</span>
                </div>
                <div style="background: #e0e0e0; height: 25px; border-radius: 12px; overflow: hidden; margin-bottom: 10px;">
                    <div style="background: {color}; height: 100%; width: {percentage}%; 
                                transition: width 0.3s ease;"></div>
                </div>
                <div style="margin-top: 10px;">
                    <p style="margin: 5px 0; color: {interp_color}; font-weight: 600;">{interpretation}</p>
                    <p style="margin: 5px 0; color: #555; font-size: 14px;"><strong>What this means:</strong> {description}</p>
                    <p style="margin: 5px 0; color: #2d3748; font-size: 14px; background: white; padding: 8px; border-radius: 4px;">
                        <strong>💡 Tip:</strong> {tip}
                    </p>
                </div>
            </div>
            """

        html += "</div>"
        return html

    def _format_skills(self, analysis: CVAnalysis) -> str:
        """Format skills analysis section."""
        html = "<div style='padding: 15px;'>"

        total_matching = len(analysis.match_score.matching_skills)
        total_missing = len(analysis.match_score.missing_skills)
        total_skills = total_matching + total_missing

        if total_skills > 0:
            match_percentage = (total_matching / total_skills) * 100
            html += f"""
            <div style='background: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
                <h4 style='margin: 0 0 10px 0; color: #1e40af;'>Skills Overview</h4>
                <p style='margin: 5px 0;'>🎯 You have <strong>{total_matching} out of {total_skills}</strong> key skills mentioned in the job description ({match_percentage:.0f}%)</p>
                <p style='margin: 5px 0; color: #666; font-size: 14px;'>Focus on developing the missing skills to increase your competitiveness for this role.</p>
            </div>
            """

        # Matching skills
        if analysis.match_score.matching_skills:
            html += "<h3 style='color: #38a169; margin-top: 20px;'>✓ Skills You Have</h3>"
            html += "<p style='color: #666; margin-bottom: 10px;'>These skills from the job description are present in your CV. Great job!</p>"
            html += "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 25px;'>"
            for i, skill in enumerate(analysis.match_score.matching_skills[:20]):
                html += f"""
                <span style="background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%); 
                            color: #22543d; padding: 8px 14px; border-radius: 20px; 
                            font-size: 14px; font-weight: 500; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    ✓ {skill}
                </span>
                """
            if len(analysis.match_score.matching_skills) > 20:
                html += f"<span style='color: #666; padding: 8px;'>... and {len(analysis.match_score.matching_skills) - 20} more</span>"
            html += "</div>"

        # Missing skills
        if analysis.match_score.missing_skills:
            html += "<h3 style='color: #e53e3e; margin-top: 25px;'>⚠ Skills to Develop or Highlight</h3>"
            html += "<p style='color: #666; margin-bottom: 10px;'>These important skills from the job description are not clearly visible in your CV.</p>"
            html += """<div style='background: #fff5f5; padding: 12px; border-radius: 8px; margin-bottom: 10px;'>
                <p style='margin: 0; color: #c53030; font-size: 14px;'>
                    <strong>💡 Action Items:</strong><br/>
                    • If you have these skills, add them to your CV<br/>
                    • If you don't, consider learning them or finding related experience<br/>
                    • Use the exact terminology from the job description
                </p>
            </div>"""
            html += "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px;'>"
            for skill in analysis.match_score.missing_skills[:20]:
                html += f"""
                <span style="background: linear-gradient(135deg, #fed7d7 0%, #fcb8b8 100%); 
                            color: #742a2a; padding: 8px 14px; border-radius: 20px; 
                            font-size: 14px; font-weight: 500; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    + {skill}
                </span>
                """
            if len(analysis.match_score.missing_skills) > 20:
                html += f"<span style='color: #666; padding: 8px;'>... and {len(analysis.match_score.missing_skills) - 20} more</span>"
            html += "</div>"

        # Keywords section
        if analysis.match_score.matching_keywords or analysis.match_score.missing_keywords:
            html += "<div style='margin-top: 30px; padding: 15px; background: #fefcbf; border-radius: 8px; border-left: 4px solid #d69e2e;'>"
            html += "<h4 style='margin: 0 0 10px 0; color: #744210;'>🔑 Important Keywords</h4>"

            if analysis.match_score.matching_keywords:
                html += f"<p style='margin: 5px 0; color: #744210;'><strong>Found:</strong> {', '.join(analysis.match_score.matching_keywords[:10])}</p>"

            if analysis.match_score.missing_keywords:
                html += f"<p style='margin: 5px 0; color: #c05621;'><strong>Missing:</strong> {', '.join(analysis.match_score.missing_keywords[:10])}</p>"
                html += "<p style='margin: 10px 0 0 0; font-size: 14px; color: #744210;'>ℹ️ Try to naturally incorporate these keywords into your experience descriptions.</p>"

            html += "</div>"

        html += "</div>"
        return html

    def _format_advice(self, analysis: CVAnalysis) -> str:
        """Format formatting advice section."""
        advice = analysis.formatting_advice
        html = "<div style='padding: 15px;'>"

        html += """<div style='background: linear-gradient(135deg, #e0f2fe 0%, #bfdbfe 100%); 
                    padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3b82f6;'>
            <h4 style='margin: 0 0 10px 0; color: #1e40af;'>🎯 About This Section</h4>
            <p style='margin: 0; color: #1e3a8a; font-size: 14px;'>
                This section provides expert advice on improving your CV's structure, content, and presentation. 
                Follow these recommendations to make your CV more effective and ATS-friendly.
            </p>
        </div>"""

        # Strengths
        if advice.strengths:
            html += "<div style='margin-bottom: 25px;'>"
            html += "<h3 style='color: #38a169; display: flex; align-items: center;'>"
            html += (
                "<span style='font-size: 24px; margin-right: 8px;'>💪</span> Your CV's Strengths"
            )
            html += "</h3>"
            html += "<p style='color: #666; margin-bottom: 12px;'>These are the strong points of your CV. Keep doing these well!</p>"
            html += "<ul style='list-style: none; padding: 0;'>"
            for i, strength in enumerate(advice.strengths, 1):
                html += f"""
                <li style='margin: 12px 0; padding: 12px; background: #f0fdf4; border-radius: 6px; 
                           border-left: 3px solid #38a169;'>
                    <span style='color: #38a169; font-weight: bold; margin-right: 8px;'>{i}.</span>
                    <span style='color: #2d3748; line-height: 1.6;'>{strength}</span>
                </li>
                """
            html += "</ul></div>"

        # Weaknesses
        if advice.weaknesses:
            html += "<div style='margin-bottom: 25px;'>"
            html += "<h3 style='color: #d69e2e; display: flex; align-items: center;'>"
            html += (
                "<span style='font-size: 24px; margin-right: 8px;'>📋</span> Areas for Improvement"
            )
            html += "</h3>"
            html += "<p style='color: #666; margin-bottom: 12px;'>These aspects of your CV could be enhanced to better match the job requirements.</p>"
            html += "<ul style='list-style: none; padding: 0;'>"
            for i, weakness in enumerate(advice.weaknesses, 1):
                html += f"""
                <li style='margin: 12px 0; padding: 12px; background: #fffbeb; border-radius: 6px; 
                           border-left: 3px solid #d69e2e;'>
                    <span style='color: #d69e2e; font-weight: bold; margin-right: 8px;'>{i}.</span>
                    <span style='color: #2d3748; line-height: 1.6;'>{weakness}</span>
                </li>
                """
            html += "</ul></div>"

        # Suggestions
        if advice.suggestions:
            html += "<div style='margin-bottom: 25px;'>"
            html += "<h3 style='color: #3182ce; display: flex; align-items: center;'>"
            html += "<span style='font-size: 24px; margin-right: 8px;'>💡</span> Actionable Recommendations"
            html += "</h3>"
            html += "<p style='color: #666; margin-bottom: 12px;'>Follow these specific suggestions to improve your CV's effectiveness.</p>"
            html += "<ul style='list-style: none; padding: 0;'>"
            for i, suggestion in enumerate(advice.suggestions, 1):
                html += f"""
                <li style='margin: 12px 0; padding: 15px; background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
                           border-radius: 8px; border-left: 4px solid #3182ce; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <div style='display: flex; align-items: start;'>
                        <span style='background: #3182ce; color: white; border-radius: 50%; 
                                     width: 24px; height: 24px; display: inline-flex; align-items: center; 
                                     justify-content: center; font-weight: bold; font-size: 12px; 
                                     margin-right: 12px; flex-shrink: 0;'>{i}</span>
                        <span style='color: #1e3a8a; line-height: 1.6; font-weight: 500;'>{suggestion}</span>
                    </div>
                </li>
                """
            html += "</ul></div>"

        # Structure Feedback
        if advice.structure_feedback:
            html += f"""
            <div style='margin: 20px 0; padding: 15px; background: #e0f2fe; border-radius: 8px; 
                       border: 2px solid #38bdf8;'>
                <h4 style='margin: 0 0 10px 0; color: #0369a1; display: flex; align-items: center;'>
                    <span style='font-size: 20px; margin-right: 8px;'>🏛️</span> CV Structure Analysis
                </h4>
                <p style='margin: 0; color: #0c4a6e; line-height: 1.8;'>{advice.structure_feedback}</p>
            </div>
            """

        # Content Feedback
        if advice.content_feedback:
            html += f"""
            <div style='margin: 20px 0; padding: 15px; background: #fef3c7; border-radius: 8px; 
                       border: 2px solid #fbbf24;'>
                <h4 style='margin: 0 0 10px 0; color: #92400e; display: flex; align-items: center;'>
                    <span style='font-size: 20px; margin-right: 8px;'>📝</span> Content Quality Analysis
                </h4>
                <p style='margin: 0; color: #78350f; line-height: 1.8;'>{advice.content_feedback}</p>
            </div>
            """

        # General Tips Footer
        html += """
        <div style='margin-top: 30px; padding: 20px; background: #f8f9fa; 
                   border-radius: 10px; border: 2px solid #6366f1; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='margin: 0 0 15px 0; color: #4338ca; font-size: 18px;'>🌟 General CV Tips</h4>
            <ul style='margin: 0; padding-left: 20px; color: #1f2937; line-height: 1.9; font-size: 15px;'>
                <li style='margin-bottom: 8px;'><strong>Use action verbs</strong> to describe your achievements (e.g., "Led", "Developed", "Implemented")</li>
                <li style='margin-bottom: 8px;'><strong>Quantify your accomplishments</strong> with numbers, percentages, or metrics when possible</li>
                <li style='margin-bottom: 8px;'><strong>Tailor your CV</strong> for each application - use keywords from the job description</li>
                <li style='margin-bottom: 8px;'><strong>Keep formatting consistent</strong> and professional throughout</li>
                <li style='margin-bottom: 8px;'><strong>Proofread carefully</strong> for spelling and grammar errors</li>
                <li style='margin-bottom: 8px;'><strong>Use a clear filename</strong> like "FirstName_LastName_CV.pdf" for easy identification</li>
            </ul>
        </div>
        """

        html += "</div>"
        return html

    def _get_score_color(self, score: float) -> str:
        """Get color for score display based on value."""
        if score >= 80:
            return "#38a169"  # Green
        elif score >= 60:
            return "#d69e2e"  # Yellow
        elif score >= 40:
            return "#dd6b20"  # Orange
        else:
            return "#e53e3e"  # Red

    def launch(self, share: bool = False, server_name: str = "127.0.0.1", server_port: int = 7860):
        """
        Launch the Gradio web interface.

        Args:
            share: If True, creates a public URL
            server_name: Server host address
            server_port: Server port number
        """
        # Create Gradio interface
        with gr.Blocks(title="CV Matcher - AI-Powered CV Analysis", theme=gr.themes.Soft()) as app:
            gr.Markdown(
                """
                # 🎯 CV Matcher - AI-Powered CV Analysis
                
                Upload your CV and provide a job description to get an AI-powered analysis of how well 
                your CV matches the job requirements. Get detailed scores, identify missing skills, 
                and receive expert formatting advice.
                
                **✨ Features:**
                - Powered by OpenAI GPT-4 for accurate analysis
                - Detailed match scoring
                - Skills gap analysis
                - Professional formatting advice
                """
            )

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Upload CV")
                    cv_input = gr.File(
                        label="Upload CV (PDF)", file_types=[".pdf"], type="filepath"
                    )

                    gr.Markdown("### 💼 Job Information")
                    job_desc_input = gr.Textbox(
                        label="Job Description",
                        placeholder="Paste the job description here...",
                        lines=10,
                    )

                    job_url_input = gr.Textbox(
                        label="Or Job URL (optional)", placeholder="https://example.com/job-posting"
                    )

                    analyze_btn = gr.Button("🔍 Analyze CV", variant="primary", size="lg")

                    gr.Markdown(
                        """
                        ---
                        **Note:** Make sure your OPENAI_API_KEY environment variable is set.
                        You can set it with: `export OPENAI_API_KEY='your-key-here'`
                        """
                    )

                with gr.Column(scale=2):
                    gr.Markdown("### 📊 Analysis Results")

                    summary_output = gr.HTML(label="Summary")

                    with gr.Tabs():
                        with gr.Tab("📈 Scores"):
                            scores_output = gr.HTML()

                        with gr.Tab("🎯 Skills Analysis"):
                            skills_output = gr.HTML()

                        with gr.Tab("💡 Formatting Advice"):
                            advice_output = gr.HTML()

                        with gr.Tab("📋 JSON Export"):
                            json_output = gr.Code(language="json", label="Full Analysis (JSON)")

            # Connect the analyze button
            analyze_btn.click(
                fn=self.analyze_cv_ui,
                inputs=[cv_input, job_desc_input, job_url_input],
                outputs=[summary_output, scores_output, skills_output, advice_output, json_output],
            )

            gr.Markdown(
                """
                ---
                <div style="text-align: center; color: #666;">
                    <p>Made with ❤️ using CV Matcher | Powered by local AI models</p>
                    <p>No data is sent to external servers - everything runs locally on your machine</p>
                </div>
                """
            )

        # Launch the app
        print(f"\n🚀 Launching CV Matcher UI on http://{server_name}:{server_port}")
        app.launch(share=share, server_name=server_name, server_port=server_port, show_error=True)


def launch_ui(
    use_local_model: bool = False,
    model_name: str = "microsoft/Phi-3-mini-4k-instruct",
    share: bool = False,
    port: int = 7860,
):
    """
    Convenience function to launch the CV Matcher UI.

    Args:
        use_local_model: Whether to use local models (True) or OpenAI (False)
        model_name: Hugging Face model to use if use_local_model=True
        share: If True, creates a public URL
        port: Port to run the server on
    """
    ui = CVMatcherUI(use_local_model=use_local_model, model_name=model_name)
    ui.launch(share=share, server_port=port)


if __name__ == "__main__":
    launch_ui()
