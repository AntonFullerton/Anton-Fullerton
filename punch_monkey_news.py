#!/usr/bin/env python3
"""
Punch the Monkey News Tracker
Fetches press, updates, and notable news about Punch the Monkey
using the Claude AI to surface relevant information.
"""

import os
import sys
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import box

console = Console()

SYSTEM_PROMPT = """You are a knowledgeable assistant who specialises in tracking
news and updates about Punch the Monkey — the real animal, NOT anything to do
with cryptocurrency, blockchain, or "Punch The Monkey" crypto tokens.

When asked for updates about Punch the Monkey, provide:
1. Notable press coverage or media mentions
2. Any significant events or milestones
3. Current known status/welfare if available
4. Where people can follow his latest news (e.g. sanctuary/zoo social pages)

Be specific about dates where known. If you are unsure of very recent news,
state that clearly. Keep responses concise, factual, and well-structured using
markdown. Always clarify which specific Punch the Monkey you are referring to
(e.g. a sanctuary animal, a zoo animal, a media-famous primate, etc.)."""

INITIAL_QUERY = """Give me a full briefing on Punch the Monkey. I want:
- Who he is and where he lives/lived
- Any notable press coverage or media stories about him
- Recent news or updates about his condition and welfare
- Where I can follow ongoing updates about him
- Anything else noteworthy about him

Do not include anything about cryptocurrency. Focus entirely on the animal."""


def get_api_key() -> str:
    """Get the Anthropic API key from environment."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        console.print(
            Panel(
                "[red]ANTHROPIC_API_KEY environment variable is not set.[/red]\n\n"
                "Set it with:\n"
                "  [cyan]export ANTHROPIC_API_KEY='your-key-here'[/cyan]\n\n"
                "Get a key at: [cyan]https://console.anthropic.com[/cyan]",
                title="Missing API Key",
                border_style="red",
            )
        )
        sys.exit(1)
    return key


def fetch_monkey_update(client: anthropic.Anthropic, query: str) -> str:
    """Send a query to Claude and return the response text."""
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": query}],
    )
    return response.content[0].text


def display_header() -> None:
    """Print the app header."""
    title = Text("Punch the Monkey - News & Updates", style="bold magenta")
    subtitle = Text("Press briefing | Current status | Notable events", style="dim")
    console.print()
    console.print(Panel(f"{title}\n{subtitle}", border_style="magenta", box=box.DOUBLE_EDGE))
    console.print()


def display_update(content: str, title: str = "Latest Briefing") -> None:
    """Render a markdown update in a styled panel."""
    md = Markdown(content)
    console.print(Panel(md, title=f"[bold green]{title}[/bold green]", border_style="blue", box=box.ROUNDED))
    console.print()


def interactive_mode(client: anthropic.Anthropic) -> None:
    """Allow follow-up questions in an interactive loop."""
    history: list[dict] = [{"role": "user", "content": INITIAL_QUERY}]

    # Get the initial briefing
    console.print("[dim]Fetching briefing from Claude...[/dim]\n")
    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=history,
        )
    except anthropic.APIError as e:
        console.print(f"[red]API error: {e}[/red]")
        sys.exit(1)

    initial_reply = response.content[0].text
    history.append({"role": "assistant", "content": initial_reply})
    display_update(initial_reply, "Latest Briefing on Punch the Monkey")

    # Follow-up loop
    console.print("[dim]Ask a follow-up question about Punch the Monkey, or type [bold]quit[/bold] to exit.[/dim]\n")
    while True:
        try:
            user_input = console.input("[bold cyan]> [/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q", "bye"}:
            console.print("[dim]Goodbye.[/dim]")
            break

        history.append({"role": "user", "content": user_input})
        console.print("[dim]Thinking...[/dim]")

        try:
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=history,
            )
        except anthropic.APIError as e:
            console.print(f"[red]API error: {e}[/red]")
            continue

        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        display_update(reply, "Response")


def main() -> None:
    display_header()
    api_key = get_api_key()
    client = anthropic.Anthropic(api_key=api_key)
    interactive_mode(client)


if __name__ == "__main__":
    main()
