# Investment Monitor

Personal investment monitoring and alerting system.

## Components

- `src/` — Python application
- `config/` — watchlists and configuration
- `data/` — local runtime data
- `.env` — private credentials (never commit this file)

## Setup

Install dependencies:

    pip install -r requirements.txt

Create `.env` from `.env.example` and add your credentials.

Run the Telegram bot:

    python -m src.bot
