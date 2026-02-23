# Punch the Monkey News Tracker

A small CLI app that surfaces press, updates, and notable news about **Punch the Monkey** (the animal — nothing to do with crypto).

## What it does

- Gives you an instant briefing on who Punch the Monkey is
- Surfaces notable press coverage and media mentions
- Reports on current welfare/status where known
- Lets you ask follow-up questions interactively

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY='your-key-here'
```

Get a key at <https://console.anthropic.com>.

## Run

```bash
python3 punch_monkey_news.py
```

You'll get an initial briefing, then a prompt to ask follow-up questions. Type `quit` to exit.
