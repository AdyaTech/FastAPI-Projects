# 🍨 Dollop

![PRs welcome](https://img.shields.io/badge/PRs-welcome-ff69b4.svg) ![Good first issues](https://img.shields.io/badge/good%20first%20issues-yes-2536d9.svg) ![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

A small-batch gelato shop website with an AI **Flavor Lab**. Describe your mood, and it builds you a cup from today's flavors.

Built with **FastAPI** and plain **HTML, CSS and JavaScript**. No frontend framework, no build step.

## Features

- **Flavor Lab (AI):** type *"rainy evening, nothing too sweet"* or *"dairy-free, under ₹300"* and get a named cup with a reason for every scoop.
- **Tweak it:** ask for changes like *"swap the coffee"* or *"make it cheaper"*. It remembers the conversation.
- **Visual order cup:** scoops stack up in each flavor's color as you add them.
- **Menu API:** 18 items across gelato, sorbet (dairy-free) and toppers, with search and filters.
- **Works offline:** no API key needed. A built-in taste matcher takes over when the AI isn't available.
- **Responsive:** the cup becomes a bottom tray on phones.

## How the Flavor Lab works

1. With a `GROQ_API_KEY`, the backend sends today's menu and your request to Llama 3.3 on [Groq](https://groq.com) and asks for a JSON cup.
2. Without a key, or if Groq fails, a local taste matcher builds the cup instead.
3. Either way, the server checks every answer against the real menu. Invented flavors, sold-out flavors, repeats and blown budgets are fixed before the website sees them.
4. Requests are rate limited per visitor (15 a minute) to protect your API key.

## Getting started

You need Python 3.10 or newer.

```bash
# 1. Create and enter a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install packages
pip install -r requirements-dev.txt

# 3. (Optional) turn on the real AI
cp .env.example .env               # Windows: copy .env.example .env
# open .env and paste your key after GROQ_API_KEY=

# 4. Run
uvicorn main:app --reload
```

Open http://127.0.0.1:8000. The interactive API docs are at http://127.0.0.1:8000/docs.

Get a free Groq key at https://console.groq.com/keys.

## API

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/menu` | Whole menu. Filters: `?category=sorbet`, `?vegan=true` |
| GET | `/menu/{id}` | One item |
| GET | `/ai/status` | Real AI or offline matcher |
| GET | `/ai/featured` | Cup of the day |
| POST | `/ai/compose` | `{"message": "...", "history": [...]}` returns a cup |

## Project structure

```
data.py          the freezer: flavors, prices, what's sold out
ai.py            Flavor Lab: prompt, Groq call, offline matcher, safety checks
main.py          FastAPI routes
models.py        request and response models
test_main.py     tests
static/          the website (index.html, css/style.css, js/app.js)
```

## Tests

```bash
pytest
```

## Contributing

Contributions are welcome, and beginners are especially welcome. You don't need an API key to help.

Easy ways to start:

- Add a new flavor in `data.py`
- Teach the offline matcher new mood words in `ai.py`
- Improve a description or fix a typo
- Add a test
- Try the site with only a keyboard and report anything awkward

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the steps, and look for issues labelled **good first issue**.
Bigger ideas: real checkout, saved favorite cups, streaming the AI reply, a dark theme.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md). If this project helped you, a ⭐ is much appreciated!

## License

MIT
