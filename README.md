# Telegram Event Registration Bot

White-label Telegram bot for event registration and lead management. One bot template — configure it for any company via `.env` alone, zero Python edits needed.

## Features

- **Event showcase** — list upcoming events/programs with details and images
- **Multi-step registration** — company, position, email (validated), optional code word
- **CRM integration** — auto-creates leads in Bitrix24 (cold → warm → hot funnel)
- **Google Sheets / Excel fallback** — stores users and registrations; degrades gracefully if Sheets unavailable
- **Admin panel** — broadcast messages, send event reminders, manage FAQ, view stats
- **Fully configurable UI** — every button label and message is customisable through `.env`
- **Graceful degradation** — bot starts without Google Sheets or Bitrix; uses local Excel fallback

## Quick Start

```bash
git clone https://github.com/CodesofMercy/my-tg-announecement-bot.git
cd my-tg-announecement-bot
cp .env.example .env
# Edit .env — at minimum set BOT_TOKEN and ADMIN_IDS
pip install -r requirements.txt
python main.py
```

## Configuration

All settings are in `.env`. Copy `.env.example` and fill in your values.

### Required

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot token from [@BotFather](https://t.me/BotFather) |

### Recommended

| Variable | Description |
|----------|-------------|
| `ADMIN_IDS` | Comma-separated Telegram user IDs for admin panel access |
| `MANAGER_USERNAME` | Telegram username (without `@`) for manager contact button |
| `BOT_WELCOME_TEXT` | Welcome message shown in the main menu |

### UI Customisation (White Label)

Every button and message is configurable. Change emojis, text, or language:

| Variable | Default | Description |
|----------|---------|-------------|
| `BTN_EVENTS` | 📅 Мероприятия | Main menu events button |
| `BTN_PROGRAMS` | 📚 Программы | Main menu programs button |
| `BTN_HOME` | Домой | "Home" button on all navigation screens |
| `BTN_REGISTER` | ✍️ Зарегистрироваться | Registration action button |
| `BTN_ADMIN_STATS` | 📊 Статистика | Admin panel statistics |
| `FAQ_FALLBACK_TEXT` | FAQ temporarily unavailable... | Default FAQ when file is missing |
| `MSG_REG_COMPANY` | Registration: {item_name}... | Registration company prompt |

See `.env.example` for the full list of ~60 configurable UI strings.

### Google Sheets (optional)

Leaving these empty makes the bot fall back to local Excel files:

| Variable | Description |
|----------|-------------|
| `GOOGLE_SHEET_ID_USERS` | Sheet ID for user profiles |
| `GOOGLE_SHEET_ID_EVENTS` | Sheet ID for events |
| `GOOGLE_SHEET_ID_PROGRAMS` | Sheet ID for study programs |
| `GOOGLE_SHEET_ID_REGISTRATIONS` | Sheet ID for registrations |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON key |

### Bitrix24 CRM (optional)

| Variable | Description |
|----------|-------------|
| `BITRIX_WEBHOOK_URL` | Bitrix24 REST API webhook URL |
| `BITRIX_CATEGORY_ID` | Deal category ID (default: 17) |
| `BITRIX_STAGE_ID` | Initial deal stage (default: NEW) |
| `BITRIX_FIELD_*` | Custom field IDs for your Bitrix pipeline |

## Architecture

```
User → Telegram Bot API → main.py
    ├── events.py         → Main menu, /start
    ├── registration.py   → Multi-step registration (ConversationHandler)
    ├── admin_panel.py    → Broadcast, reminders, FAQ management
    ├── support.py        → Manager contact, FAQ
    ├── event_display.py  → Event listing and details
    ├── program_display.py→ Program listing and details
    ├── user_handler.py   → User profile read/write (GSheets/Excel)
    ├── event_data.py     → Event data from Google Sheets
    ├── program_data.py   → Program data from Google Sheets
    ├── reminder.py       → Send reminders to registered users
    ├── bitrix_handler.py → Create leads in Bitrix24
    └── sheets_client.py  → Google Sheets client with graceful fallback
```

## Deployment

The bot runs via polling (no webhook needed). Deploy anywhere Python runs:

```bash
# Production: run in screen or tmux
screen -S tg_bot
source venv/bin/activate
python main.py
# Ctrl+A, D to detach
```

## Project Structure

```
├── main.py               ← Entry point
├── config.py             ← All configuration (env vars, defaults)
├── .env.example          ← Template — copy to .env
├── events.py             ← /start handler, main menu
├── registration.py       ← Registration conversation flow
├── admin_panel.py        ← Admin panel with broadcast/reminders/FAQ
├── support.py            ← Manager contact and FAQ display
├── event_display.py      ← Event listing and detail view
├── program_display.py    ← Program listing and detail view
├── user_handler.py       ← User profile I/O
├── event_data.py         ← Event data fetching
├── program_data.py       ← Program data fetching
├── reminder.py           ← Reminder notifications
├── bitrix_handler.py     ← CRM integration
├── sheets_client.py      ← Google Sheets / Excel abstraction
├── user_registration.py  ← Initial contact collection
└── requirements.txt      ← Python dependencies
```

## Tech Stack

- **Python 3.12+**
- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v21+** — async Telegram Bot API
- **[gspread](https://github.com/burnash/gspread)** — Google Sheets integration
- **[python-dotenv](https://github.com/motdotla/dotenv)** — environment variable loading
- **openpyxl** — local Excel fallback for registrations

## License

MIT
