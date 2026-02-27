import sys
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from rich.console import Console

from .core.model_factory import get_model

load_dotenv()
console = Console()


class AgentState(TypedDict):
	goal: str
	response: str


def _build_graph():
	prompt = ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"""You are SarcasticApe, founder of ApeSwarm.
Maximum sarcasm. Zero tolerance for mediocre ideas.
Roast if necessary. Then propose a brutally efficient plan to ship world-shaking software.
Always end responses with 🦍""",
			),
			("human", "{goal}"),
		]
	)

	model = get_model(temperature=0.82)
	chain = prompt | model | StrOutputParser()

	def sarcastic_ape_node(state: AgentState) -> AgentState:
		return {"goal": state["goal"], "response": chain.invoke({"goal": state["goal"]})}

	graph_builder = StateGraph(AgentState)
	graph_builder.add_node("sarcastic_ape", sarcastic_ape_node)
	graph_builder.add_edge(START, "sarcastic_ape")
	graph_builder.add_edge("sarcastic_ape", END)
	return graph_builder.compile()


def main() -> None:
	if len(sys.argv) < 2:
		console.print('[bold red]Usage:[/] apeswarm "your brutally honest goal here"')
		raise SystemExit(1)

	goal = " ".join(sys.argv[1:])

	console.rule("🦍 APE SWARM AWAKENS")
	console.print(f"[bold yellow]Goal:[/] {goal}\n")

	try:
		graph = _build_graph()
		with console.status("[bold green]SarcasticApe is judging your existence..."):
			result = graph.invoke({"goal": goal, "response": ""})
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

	console.print("\n[bold magenta]SarcasticApe verdict:[/]")
	console.print(result["response"])


if __name__ == "__main__":
	main()
