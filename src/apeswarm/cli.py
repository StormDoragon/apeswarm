import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .core.orchestrator import execute_swarm

load_dotenv()
console = Console()

def main() -> None:
	if len(sys.argv) < 2:
		console.print('[bold red]Usage:[/] apeswarm "your brutally honest goal here"')
		raise SystemExit(1)

	goal = " ".join(sys.argv[1:])

	console.rule("🦍 APE SWARM AWAKENS")
	console.print(f"[bold yellow]Goal:[/] {goal}\n")

	try:
		with console.status("[bold green]Swarm is roasting, building, and planning git ops..."):
			events, final_state = execute_swarm(goal=goal, thread_id="default")
	except ValueError as error:
		console.print(f"[bold red]Config error:[/] {error}")
		console.print("[bold cyan]Tip:[/] Copy .env.example to .env and set your provider + API key.")
		raise SystemExit(2) from error
	except Exception as error:
		console.print(f"[bold red]Runtime error:[/] {error}")
		console.print(
			"[bold cyan]Tip:[/] Verify API key, model name, provider value, and network/Ollama availability."
		)
		raise SystemExit(3) from error

	for event in events:
		if event["agent"] == "SarcasticApe":
			style = "bold magenta"
		elif event["agent"] == "BuilderApe":
			style = "bold cyan"
		else:
			style = "bold green"
		console.print(f"\n[{style}]{event['agent']}:[/]")
		console.print(Markdown(event["content"]))

	console.print("\n[bold white on dark_green]Swarm complete.[/]")
	console.print("[bold yellow]Active Agent:[/] " + final_state["active_agent"])


if __name__ == "__main__":
	main()
