from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from apeswarm.agents import builder_ape_response, git_ape_response, sarcastic_ape_response
from apeswarm.core.model_factory import get_model


class SwarmState(TypedDict):
	goal: str
	active_agent: str
	sarcastic_output: str
	builder_output: str
	git_output: str


class SwarmEvent(TypedDict):
	agent: str
	content: str


_CHECKPOINTER = MemorySaver()
_APP = None


def _build_app():
	model = get_model()

	def sarcastic_ape_node(state: SwarmState) -> SwarmState:
		return {
			"goal": state["goal"],
			"active_agent": "BuilderApe",
			"sarcastic_output": sarcastic_ape_response(model, state["goal"]),
			"builder_output": state["builder_output"],
			"git_output": state["git_output"],
		}

	def builder_ape_node(state: SwarmState) -> SwarmState:
		return {
			"goal": state["goal"],
			"active_agent": "GitApe",
			"sarcastic_output": state["sarcastic_output"],
			"builder_output": builder_ape_response(
				model=model,
				goal=state["goal"],
				sarcastic_context=state["sarcastic_output"],
			),
			"git_output": state["git_output"],
		}

	def git_ape_node(state: SwarmState) -> SwarmState:
		return {
			"goal": state["goal"],
			"active_agent": "done",
			"sarcastic_output": state["sarcastic_output"],
			"builder_output": state["builder_output"],
			"git_output": git_ape_response(
				model=model,
				goal=state["goal"],
				builder_output=state["builder_output"],
			),
		}

	graph_builder = StateGraph(SwarmState)
	graph_builder.add_node("sarcastic_ape", sarcastic_ape_node)
	graph_builder.add_node("builder_ape", builder_ape_node)
	graph_builder.add_node("git_ape", git_ape_node)
	graph_builder.add_edge(START, "sarcastic_ape")
	graph_builder.add_edge("sarcastic_ape", "builder_ape")
	graph_builder.add_edge("builder_ape", "git_ape")
	graph_builder.add_edge("git_ape", END)
	return graph_builder.compile(checkpointer=_CHECKPOINTER)


def _get_app():
	global _APP
	if _APP is None:
		_APP = _build_app()
	return _APP


def execute_swarm(goal: str, thread_id: str = "default") -> tuple[list[SwarmEvent], SwarmState]:
	app = _get_app()
	initial_state: SwarmState = {
		"goal": goal,
		"active_agent": "SarcasticApe",
		"sarcastic_output": "",
		"builder_output": "",
		"git_output": "",
	}

	config = {"configurable": {"thread_id": thread_id}}
	events: list[SwarmEvent] = []
	current_state = initial_state.copy()

	for update in app.stream(initial_state, config=config, stream_mode="updates"):
		for node_name, patch in update.items():
			current_state.update(patch)
			if node_name == "sarcastic_ape" and patch.get("sarcastic_output"):
				events.append({"agent": "SarcasticApe", "content": patch["sarcastic_output"]})
			elif node_name == "builder_ape" and patch.get("builder_output"):
				events.append({"agent": "BuilderApe", "content": patch["builder_output"]})
			elif node_name == "git_ape" and patch.get("git_output"):
				events.append({"agent": "GitApe", "content": patch["git_output"]})

	return events, current_state