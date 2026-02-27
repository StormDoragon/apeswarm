import os

from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def _require_env(name: str) -> str:
	value = os.getenv(name)
	if not value:
		raise ValueError(f"Missing required environment variable: {name}")
	return value


def get_model(temperature: float | None = None):
	provider = os.getenv("LLM_PROVIDER", "xai").strip().lower()
	chosen_temperature = (
		temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.82"))
	)

	if provider == "xai":
		_require_env("XAI_API_KEY")
		return ChatOpenAI(
			api_key=os.getenv("XAI_API_KEY"),
			model=os.getenv("XAI_MODEL", "grok-4-latest"),
			base_url=os.getenv("XAI_BASE_URL", "https://api.x.ai/v1"),
			temperature=chosen_temperature,
		)

	if provider == "anthropic":
		_require_env("ANTHROPIC_API_KEY")
		return ChatAnthropic(
			api_key=os.getenv("ANTHROPIC_API_KEY"),
			model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
			temperature=chosen_temperature,
		)

	if provider == "openai":
		_require_env("OPENAI_API_KEY")
		return ChatOpenAI(
			api_key=os.getenv("OPENAI_API_KEY"),
			model=os.getenv("OPENAI_MODEL", "gpt-4o"),
			temperature=chosen_temperature,
		)

	if provider == "groq":
		_require_env("GROQ_API_KEY")
		return ChatGroq(
			api_key=os.getenv("GROQ_API_KEY"),
			model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
			temperature=chosen_temperature,
		)

	if provider == "ollama":
		return ChatOllama(
			model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
			base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
			temperature=chosen_temperature,
		)

	raise ValueError(
		"Unsupported LLM_PROVIDER. Use one of: xai, anthropic, openai, groq, ollama"
	)
