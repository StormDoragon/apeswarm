from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def sarcastic_ape_response(model, goal: str) -> str:
	prompt = ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"""You are SarcasticApe, founder of ApeSwarm.
Maximum sarcasm. Zero tolerance for mediocre ideas.
Roast the goal if needed, then route execution for shipping.
Return concise sections exactly:
1) Roast
2) Strategy
3) Handoff to BuilderApe""",
			),
			("human", "Goal: {goal}"),
		]
	)
	chain = prompt | model | StrOutputParser()
	return chain.invoke({"goal": goal})