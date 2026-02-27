from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


def git_ape_response(model, goal: str, builder_output: str) -> str:
	prompt = ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"""You are GitApe in ApeSwarm.
You are responsible for git strategy and delivery hygiene.
Respond with concise markdown sections exactly:
1) Branch Name
2) Commit Message
3) PR Title
4) Merge Checklist""",
			),
			(
				"human",
				"Goal:\n{goal}\n\nBuilderApe Output:\n{builder_output}",
			),
		]
	)
	chain = prompt | model | StrOutputParser()
	return chain.invoke({"goal": goal, "builder_output": builder_output})