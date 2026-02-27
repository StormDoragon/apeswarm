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

# optional flags
uv run apeswarm "ship this safely" --self-edit --self-edit-iterations 2
uv run apeswarm "prepare release" --allow-git-write --auto-confirm
```

## Choose Your Brain (`.env`)
```env
LLM_PROVIDER=xai          # xai | anthropic | openai | groq | ollama
TEMPERATURE=0.82
```

## Swarm Flow (Current)
- **SarcasticApe** roasts + routes
- **BuilderApe** proposes practical implementation steps/files
- **TruthApe** verifies claims + highlights risk
- **SelfEditApe** proposes safe self-improvement loop targets
- **GitApe** proposes branch/commit/PR strategy
- **GitExec** executes GitApe plan in dry-run by default (write mode is opt-in)

## Example Multi-Agent Run
```text
$ apeswarm "roast my decision to build in public and give a 5-step viral plan"

SarcasticApe:
- Roast
- Strategy
- Handoff to BuilderApe

BuilderApe:
- Build Plan
- Proposed File Changes
- Handoff to GitApe

GitApe:
- Branch Name: public-beta-1
- Commit Message: feat(public-beta): Initialize public beta release...
- PR Title: Public Beta Release: Unfiltered Ape Product for Your Viewing Pleasure!
- Merge Checklist
```

## Troubleshooting
- **No API key configured?** Set `LLM_PROVIDER` + matching key in `.env`.
- **Want zero-cost local runs?** Use Ollama:
	- Set `LLM_PROVIDER=ollama`
	- Set `OLLAMA_MODEL=llama3.1:8b` (or `llama3.2`)
	- Ensure Ollama is installed and running, then `ollama pull <model>`
- **Ollama too slow?** Try `groq` for fast hosted inference, or `xai` for strongest sarcasm personality.
- **GitApe capability today:** can execute real branch+commit with `--allow-git-write --auto-confirm`.

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
