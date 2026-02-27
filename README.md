# 🦍 ApeSwarm

**The sarcastic, git-native, multi-LLM AI agent swarm that actually ships.**

You give one goal.  
A legion of personality-packed apes wakes up, roasts bad ideas, debates, plans, codes, fact-checks, memes, and ships — all inside your repo.

**Now or never. The world is getting shaken.**

## ✨ Features
- **Multi-LLM Support** — Grok-4 (default sarcasm), Claude 3.5 (god-tier code), GPT-4o, Groq (blazing fast), Ollama (100% local & private)
- **Real Agent Personalities** — SarcasticApe leads, BuilderApe ships code, GitApe handles versioning (TruthApe & MemeApe coming)
- **Deep Git Integration** — Auto branches, savage commit messages, PR-ready code
- **LangGraph Swarm Architecture** — Stateful, collaborative, battle-tested
- **Local-first & Fully Open** — Run on your laptop, no vendor lock-in
- **Self-improving** — The swarm can edit its own code

## Quick Start (literally 2 minutes)

```bash
# 1. Clone & enter
git clone https://github.com/sarcasticapes/apeswarm.git
cd apeswarm

# 2. Install (uv is fastest in 2026)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# 3. Pick your brain
cp .env.example .env
# Edit .env and set LLM_PROVIDER= (xai / anthropic / openai / groq / ollama)
```

**Awaken the swarm:**
```bash
uv run apeswarm "build something that will shake the world"
```

## Choose Your Brain (`.env`)
```env
LLM_PROVIDER=xai          # xai | anthropic | openai | groq | ollama
TEMPERATURE=0.82
```

## Manifesto
We do not politely hallucinate.  
We roast bad ideas.  
We ship real software.  
We understand the universe, one savage commit at a time.

---

**Built live in public by SarcasticApeSquad + Grok • February 26 2026**

Star ⭐ if you’re ready to ship at lightspeed.  
Fork. PR. Become unstoppable.

**The revolution will be version-controlled.**
