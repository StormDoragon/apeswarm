import argparse
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from .core.orchestrator import execute_swarm

load_dotenv()
console = Console()


def _parse_args(argv: list[str]) -> argparse.Namespace:
	parser = argparse.ArgumentParser(prog="apeswarm", description="Run the ApeSwarm multi-agent CLI")
	parser.add_argument("goal", nargs="+", help="Goal for the swarm")
	parser.add_argument("--thread-id", default="apeswarm-default", help="Conversation thread id")
	parser.add_argument(
		"--allow-git-write",
		action="store_true",
		help="Allow GitApe to create/checkout branch and commit changes",
	)
	parser.add_argument(
		"--auto-confirm",
		action="store_true",
		help="Skip confirmation gate for git writes (dangerous)",
	)
	parser.add_argument(
		"--self-edit",
		action="store_true",
		help="Enable the SelfEditApe planning loop",
	)
	parser.add_argument(
		"--self-edit-iterations",
		type=int,
		default=1,
		help="Requested self-edit loop iterations",
	)
	return parser.parse_args(argv)


def main() -> None:
	if len(sys.argv) < 2:
		console.print('[bold red]Usage:[/] apeswarm "your brutally honest goal here"')
		raise SystemExit(1)

	args = _parse_args(sys.argv[1:])
	goal = " ".join(args.goal)

	console.rule("🦍 APE SWARM AWAKENS")
	console.print(f"[bold yellow]Goal:[/] {goal}\n")
	console.print(
		"[dim]"
		+ f"thread_id={args.thread_id} | "
		+ f"git_write={args.allow_git_write} | "
		+ f"auto_confirm={args.auto_confirm} | "
		+ f"self_edit={args.self_edit} ({args.self_edit_iterations})"
		+ "[/dim]\n"
	)

	try:
		with console.status("[bold green]Swarm is roasting, building, and planning git ops..."):
			events, final_state = execute_swarm(
				goal=goal,
				thread_id=args.thread_id,
				allow_git_write=args.allow_git_write,
				auto_confirm=args.auto_confirm,
				enable_self_edit=args.self_edit,
				self_edit_iterations=args.self_edit_iterations,
			)
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
		elif event["agent"] == "TruthApe":
			style = "bold bright_blue"
		elif event["agent"] == "SelfEditApe":
			style = "bold bright_white"
		elif event["agent"] == "GitExec":
			style = "bold bright_green"
		else:
			style = "bold green"
		console.print(f"\n[{style}]{event['agent']}:[/]")
		console.print(Markdown(event["content"]))

	console.print("\n[bold white on dark_green]Swarm complete.[/]")
	console.print("[bold yellow]Active Agent:[/] " + final_state["active_agent"])


if __name__ == "__main__":
	main()
