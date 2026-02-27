from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def builder_ape_response(model, goal: str, sarcastic_context: str) -> str:
	prompt = ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"""You are BuilderApe in ApeSwarm.
Convert strategy into practical implementation output.
Produce concise markdown with sections exactly:
1) Build Plan
2) Proposed File Changes
3) Handoff to GitApe""",
			),
			(
				"human",
				"Goal:\n{goal}\n\nSarcasticApe Guidance:\n{sarcastic_context}",
			),
		]
	)
	chain = prompt | model | StrOutputParser()
	return chain.invoke({"goal": goal, "sarcastic_context": sarcastic_context})