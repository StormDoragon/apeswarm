from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def self_edit_ape_response(model, goal: str, truth_output: str, iterations: int) -> str:
	prompt = ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"""You are SelfEditApe in ApeSwarm.
You design safe self-improvement loops for the repository.
Do not pretend files were modified.
Return concise markdown sections exactly:
1) Self-Edit Loop Plan
2) First Iteration Patch Targets
3) Safety Guardrails
4) Handoff to GitApe""",
			),
			(
				"human",
				"Goal:\n{goal}\n\nTruthApe Findings:\n{truth_output}\n\nRequested Iterations: {iterations}",
			),
		]
	)
	chain = prompt | model | StrOutputParser()
	return chain.invoke({"goal": goal, "truth_output": truth_output, "iterations": iterations})