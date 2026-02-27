from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from apeswarm.agents import (
	builder_ape_response,
	git_ape_response,
	sarcastic_ape_response,
	self_edit_ape_response,
	truth_ape_response,
)
from apeswarm.core.git_executor import execute_git_plan
from apeswarm.core.model_factory import get_model
from apeswarm.core.search import collect_repo_context


class SwarmState(TypedDict):
	goal: str
	active_agent: str
	allow_git_write: bool
	auto_confirm: bool
	enable_self_edit: bool
	self_edit_iterations: int
	sarcastic_output: str
	builder_output: str
	truth_output: str
	self_edit_output: str
	git_output: str
	git_exec_output: str
	search_context: str


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
			"allow_git_write": state["allow_git_write"],
			"auto_confirm": state["auto_confirm"],
			"enable_self_edit": state["enable_self_edit"],
			"self_edit_iterations": state["self_edit_iterations"],
			"sarcastic_output": sarcastic_ape_response(model, state["goal"]),
			"builder_output": state["builder_output"],
			"truth_output": state["truth_output"],
			"self_edit_output": state["self_edit_output"],
			"git_output": state["git_output"],
			"git_exec_output": state["git_exec_output"],
			"search_context": state["search_context"],
		}

	def builder_ape_node(state: SwarmState) -> SwarmState:
		return {
			"goal": state["goal"],
			"active_agent": "TruthApe",
			"allow_git_write": state["allow_git_write"],
			"auto_confirm": state["auto_confirm"],
			"enable_self_edit": state["enable_self_edit"],
			"self_edit_iterations": state["self_edit_iterations"],
			"sarcastic_output": state["sarcastic_output"],
			"builder_output": builder_ape_response(
				model=model,
				goal=state["goal"],
				sarcastic_context=state["sarcastic_output"],
			),
			"truth_output": state["truth_output"],
			"self_edit_output": state["self_edit_output"],
			"git_output": state["git_output"],
			"git_exec_output": state["git_exec_output"],
			"search_context": state["search_context"],
		}

	def truth_ape_node(state: SwarmState) -> SwarmState:
		return {
			"goal": state["goal"],
			"active_agent": "SelfEditApe",
			"allow_git_write": state["allow_git_write"],
			"auto_confirm": state["auto_confirm"],
			"enable_self_edit": state["enable_self_edit"],
			"self_edit_iterations": state["self_edit_iterations"],
			"sarcastic_output": state["sarcastic_output"],
			"builder_output": state["builder_output"],
			"truth_output": truth_ape_response(
				model=model,
				goal=state["goal"],
				builder_output=state["builder_output"],
				search_context=state["search_context"],
			),
			"self_edit_output": state["self_edit_output"],
			"git_output": state["git_output"],
			"git_exec_output": state["git_exec_output"],
			"search_context": state["search_context"],
		}

	def self_edit_ape_node(state: SwarmState) -> SwarmState:
		if not state["enable_self_edit"]:
			self_edit_output = "Self-edit loop disabled for this run."
		else:
			self_edit_output = self_edit_ape_response(
				model=model,
				goal=state["goal"],
				truth_output=state["truth_output"],
				iterations=state["self_edit_iterations"],
			)
		return {
			"goal": state["goal"],
			"active_agent": "GitApe",
			"allow_git_write": state["allow_git_write"],
			"auto_confirm": state["auto_confirm"],
			"enable_self_edit": state["enable_self_edit"],
			"self_edit_iterations": state["self_edit_iterations"],
			"sarcastic_output": state["sarcastic_output"],
			"builder_output": state["builder_output"],
			"truth_output": state["truth_output"],
			"self_edit_output": self_edit_output,
			"git_output": state["git_output"],
			"git_exec_output": state["git_exec_output"],
			"search_context": state["search_context"],
		}

	def git_ape_node(state: SwarmState) -> SwarmState:
		git_output = git_ape_response(
			model=model,
			goal=state["goal"],
			builder_output=state["builder_output"] + "\n\n" + state["self_edit_output"],
		)
		git_exec_output = execute_git_plan(
			git_plan_markdown=git_output,
			repo_root=Path.cwd(),
			allow_write=state["allow_git_write"],
			auto_confirm=state["auto_confirm"],
		)
		return {
			"goal": state["goal"],
			"active_agent": "done",
			"allow_git_write": state["allow_git_write"],
			"auto_confirm": state["auto_confirm"],
			"enable_self_edit": state["enable_self_edit"],
			"self_edit_iterations": state["self_edit_iterations"],
			"sarcastic_output": state["sarcastic_output"],
			"builder_output": state["builder_output"],
			"truth_output": state["truth_output"],
			"self_edit_output": state["self_edit_output"],
			"git_output": git_output,
			"git_exec_output": git_exec_output,
			"search_context": state["search_context"],
		}

	graph_builder = StateGraph(SwarmState)
	graph_builder.add_node("sarcastic_ape", sarcastic_ape_node)
	graph_builder.add_node("builder_ape", builder_ape_node)
	graph_builder.add_node("truth_ape", truth_ape_node)
	graph_builder.add_node("self_edit_ape", self_edit_ape_node)
	graph_builder.add_node("git_ape", git_ape_node)
	graph_builder.add_edge(START, "sarcastic_ape")
	graph_builder.add_edge("sarcastic_ape", "builder_ape")
	graph_builder.add_edge("builder_ape", "truth_ape")
	graph_builder.add_edge("truth_ape", "self_edit_ape")
	graph_builder.add_edge("self_edit_ape", "git_ape")
	graph_builder.add_edge("git_ape", END)
	return graph_builder.compile(checkpointer=_CHECKPOINTER)


def _get_app():
	global _APP
	if _APP is None:
		_APP = _build_app()
	return _APP


def execute_swarm(
	goal: str,
	thread_id: str = "default",
	allow_git_write: bool = False,
	auto_confirm: bool = False,
	enable_self_edit: bool = False,
	self_edit_iterations: int = 1,
) -> tuple[list[SwarmEvent], SwarmState]:
	app = _get_app()
	search_context = collect_repo_context(goal=goal, repo_root=Path.cwd())
	initial_state: SwarmState = {
		"goal": goal,
		"active_agent": "SarcasticApe",
		"allow_git_write": allow_git_write,
		"auto_confirm": auto_confirm,
		"enable_self_edit": enable_self_edit,
		"self_edit_iterations": max(1, self_edit_iterations),
		"sarcastic_output": "",
		"builder_output": "",
		"truth_output": "",
		"self_edit_output": "",
		"git_output": "",
		"git_exec_output": "",
		"search_context": search_context,
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
			elif node_name == "truth_ape" and patch.get("truth_output"):
				events.append({"agent": "TruthApe", "content": patch["truth_output"]})
			elif node_name == "self_edit_ape" and patch.get("self_edit_output"):
				events.append({"agent": "SelfEditApe", "content": patch["self_edit_output"]})
			elif node_name == "git_ape" and patch.get("git_output"):
				events.append({"agent": "GitApe", "content": patch["git_output"]})
				if patch.get("git_exec_output"):
					events.append({"agent": "GitExec", "content": patch["git_exec_output"]})

	return events, current_state