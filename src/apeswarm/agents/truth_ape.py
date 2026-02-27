from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def truth_ape_response(model, goal: str, builder_output: str, search_context: str) -> str:
	prompt = ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"""You are TruthApe in ApeSwarm.
Your job is to verify claims and reduce nonsense.
Be blunt but precise.
Return concise markdown sections exactly:
1) Verified
2) Needs Evidence
3) Risks
4) Handoff to SelfEditApe""",
			),
			(
				"human",
				"Goal:\n{goal}\n\nBuilderApe Output:\n{builder_output}\n\nRepository Search Context:\n{search_context}",
			),
		]
	)
	chain = prompt | model | StrOutputParser()
	return chain.invoke(
		{
			"goal": goal,
			"builder_output": builder_output,
			"search_context": search_context,
		}
	)