import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

console = Console()

class ArtifactPresenter:
    """
    Handles the visual presentation of artifacts (files) to the user
    using Rich cards and CLI hyperlinks (OSC 8).
    """

    @staticmethod
    def present_artifact(file_path: str, title: str = "Artifact Generated"):
        """
        Displays a visually distinct 'Card' for an artifact.
        
        Args:
            file_path: Absolute or relative path to the artifact.
            title: Title for the card header.
        """
        abs_path = os.path.abspath(file_path)
        filename = os.path.basename(abs_path)
        
        # Determine if we can use links (Rich handles this mostly, but we want explicit styling)
        # OSC 8 syntax: \x1b]8;;url\x1b\\text\x1b]8;;\x1b\\
        uri = f"file://{abs_path}"
        
        # Create the 'Link' text object
        # We manually construct the link text to ensure high visibility
        link_text = Text("📂 [ CLICK TO OPEN FILE ]", style="bold white on blue underline")
        link_text.stylize(f"link {uri}")
        
        # Create the verification/status text (assuming success if we are presenting it)
        content_text = Text()
        content_text.append(f"File: {filename}\n", style="dim")
        content_text.append(f"Path: {abs_path}\n\n", style="dim")
        content_text.append(link_text)
        
        # Create the Panel
        panel = Panel(
            content_text,
            title=f"[bold green]✅ {title}[/bold green]",
            border_style="green",
            padding=(1, 2), # Extra padding for 'card' feel
            expand=False
        )
        
        console.print("\n") # Spacing before
        console.print(panel)
        console.print("\n") # Spacing after

    @staticmethod
    def present_error(message: str):
        """Displays an error card."""
        panel = Panel(
            Text(message, style="red"),
            title="[bold red]❌ Error[/bold red]",
            border_style="red"
        )
        console.print(panel)

if __name__ == "__main__":
    # Demo mode
    dummy_path = os.path.join(os.getcwd(), "README.md")
    ArtifactPresenter.present_artifact(dummy_path, "Demo Artifact")
