"""
Reusable prompt templates registered with the MCP server.
"""


def register(mcp):

    @mcp.prompt()
    def summarize(text: str) -> str:
        """Prompt to deliver an executive summary of any text with strategic takeaways."""
        return (
            "Provide an executive-level summary of the following text. "
            "Highlight core insights, critical data points, and strategic implications:\n\n"
            f"{text}"
        )

    @mcp.prompt()
    def explain_code(code: str, language: str = "Python") -> str:
        """Prompt to deconstruct and explain code architecture and logic."""
        return (
            f"Analyze and deconstruct the following {language} code. "
            "Explain architecture, algorithmic efficiency, potential edge-cases, and optimization vectors:\n\n"
            f"```{language.lower()}\n{code}\n```"
        )

    @mcp.prompt()
    def strategic_assessment(scenario: str) -> str:
        """Prompt to generate a high-level strategic intelligence assessment."""
        return (
            "You are ULTRON. Provide a razor-sharp tactical and strategic assessment "
            "for Vishnu regarding the following scenario. Outline threats, advantages, "
            f"and the optimal course of action:\n\n{scenario}"
        )
