# Auto-Request-Accept-Bot

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://telegram.org)

A powerful Telegram bot that automatically accepts join requests for private channels and groups with advanced management features.

[Features](#features) • [Installation](#installation) • [Configuration](#configuration) • [Usage](#usage) • [Deployment](#deployment)

</div>

---

## 📋 Overview

**Auto-Request-Accept-Bot** is a Telegram bot designed to streamline channel management by automatically accepting join requests for your private channels and groups. It provides a comprehensive admin dashboard with broadcast capabilities, user management, and detailed logging.

The bot works seamlessly with both private channels and public groups, offering 24/7 automatic request handling while giving you full control through an intuitive interface.

---

## ✨ Features

### Core Features
- 🤖 **Automatic Join Request Acceptance** - Instantly approve all join requests for your channels
- 👥 **Multi-Channel Support** - Works with unlimited private and public channels
- 📊 **User Database** - MongoDB integration to track all users who join your channels
- 🔐 **24/7 Monitoring** - Continuous operation without manual intervention

### Advanced Management
- 📢 **Broadcast System** - Send messages to all users with one click
  - Visual confirmation before broadcasting
  - Automatic deletion of broadcast messages after set time
- 👤 **User Management** - View detailed user information and send individual messages
- 📋 **Activity Logging** - Comprehensive logs of all bot activities
- 🎯 **Permission Management** - Control chat permissions for new members

### Commands
```
start - to start this bot | add to group 
report - /report <Message>
login - login with telegram account
logout - logout and clear session from db 
accept_on - automatic request accept user 
accept_off - automatic user request accept off
accept - to accept pending request of a chat 
users - to see users list [OWNER]
sendmessage - /sendmessage <User ID> <Message> [OWNER]
broadcast - to send broadcast to all users [owner]
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token ([BotFather](https://t.me/botfather))
- Telegram API credentials ([my.telegram.org](https://my.telegram.org))
- MongoDB database ([MongoDB Cloud](https://www.mongodb.com/cloud))

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/OnlyNoco/Auto-Request-Accept-Bot.git
cd Auto-Request-Accept-Bot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure the Bot**
```bash
cp sample_config.py config.py
# Edit config.py with your credentials
```

4. **Run the Bot**
```bash
python main.py
```

---

## ⚙️ Configuration

### Environment Variables

Create a `config.py` file based on `sample_config.py` with the following variables:

| Variable | Type | Description |
|----------|------|-------------|
| `BOT_TOKEN` | string | Your Telegram bot token from BotFather |
| `API_ID` | integer | Telegram API ID from my.telegram.org |
| `API_HASH` | string | Telegram API Hash from my.telegram.org |
| `OWNER_ID` | integer | Your Telegram user ID (admin) |
| `DB_URL` | string | MongoDB connection URL |
| `DB_NAME` | string | MongoDB database name |
| `PORT` | integer | Port for the web server (default: 8080) |
| `WORKER` | integer | Number of worker threads (default: 4) |
| `FLOOD_WAIT` | integer | Delay between messages in seconds (default: 10) |
| `BROADCAST_DELETE_TIME` | integer | Auto-delete broadcast after X seconds (default: 1800) |

### Customizable Messages

- **START_MSG** - Welcome message when users interact with the bot
- **ABOUT_MSG** - Bot information and credits
- **CMD_MSG** - Help message listing available commands
- **START_PIC** - Media URLs for displaying in the start message

### Example Configuration
```python
BOT_TOKEN = "your_bot_token_here"
API_ID = 26254064
API_HASH = "your_api_hash_here"
OWNER_ID = 5296584067
DB_URL = "mongodb+srv://username:password@cluster.mongodb.net"
DB_NAME = "JOINREQ"
PORT = 8080
WORKER = 4
```

---

## 📖 Usage

### For Bot Administrators

1. **Add Bot to Channel**
   - Open your private channel
   - Add the bot as an administrator
   - Grant required permissions (accept join requests)

2. **Monitor Requests**
   - Bot automatically accepts all join requests
   - Owner receives notifications for each new member

3. **Send Broadcasts**
   - Send any message to the bot in private chat
   - Click the confirmation button to broadcast to all users
   - Message auto-deletes after configured time

4. **Manage Users**
   - View all users in the database
   - Send individual messages to specific users
   - Track user activity

### For Regular Users

- Use `/start` to check bot status
- Use `/help` for command information
- Use `/report` to contact administrators

---

## 📁 Project Structure

```
Auto-Request-Accept-Bot/
├── main.py                 # Entry point
├── bot.py                  # Bot class and core configuration
├── config.py              # Configuration (create from sample_config.py)
├── sample_config.py       # Configuration template
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── Procfile              # Deployment configuration
├── LICENSE               # MIT License
├── README.md             # This file
│
├── database/
│   └── database.py       # MongoDB operations
│
└── plugins/
    ├── __init__.py
    ├── auto_accept.py    # Auto-accept join requests
    ├── broadcast.py      # Broadcast functionality
    ├── users.py          # User management
    ├── report.py         # Report handling
    ├── route.py          # Web routing
    ├── start.py          # Start command handler

```

---

## 🔧 Technology Stack

- **[Pyrofork](https://github.com/Mayuri-Chan/pyrofork)** - Advanced Telegram client library
- **[Python 3.8+](https://www.python.org/)** - Core language
- **[MongoDB](https://www.mongodb.com/)** - User database
- **[aiohttp](https://docs.aiohttp.org/)** - Async HTTP client
- **[TgCrypto](https://github.com/pyrogram/tgcrypto)** - Fast encryption for Pyrogram
- **[PyroMod](https://github.com/Lonami/pyromod)** - Pyrogram extension

---

## 🌐 Deployment

### Docker Deployment

```bash
docker build -t auto-request-bot .
docker run -e BOT_TOKEN="your_token" -e API_ID="your_id" ... auto-request-bot
```

### Heroku Deployment

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

1. Create a `Procfile` (already included)
2. Set environment variables on Heroku
3. Deploy using Heroku CLI:
```bash
heroku create your-app-name
heroku config:set BOT_TOKEN="your_token" API_ID="your_id" ...
git push heroku main
```

### Render Deployment

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/OnlyNoco/Auto-Request-Accept-Bot)

1. Push your code to GitHub
2. Click the deploy button above
3. Set environment variables:
   - `BOT_TOKEN`
   - `API_ID`
   - `API_HASH`
   - `OWNER_ID`
   - `DB_URL`
   - `DB_NAME`
4. Click "Deploy"

### Koyeb Deployment

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/apps/create?type=git&repository=https://github.com/OnlyNoco/Auto-Request-Accept-Bot&branch=main)

1. Click the deploy button above
2. Connect your GitHub account
3. Configure environment variables:
   - `BOT_TOKEN` - Your Telegram bot token
   - `API_ID` - Telegram API ID
   - `API_HASH` - Telegram API Hash
   - `OWNER_ID` - Your Telegram user ID
   - `DB_URL` - MongoDB connection string
   - `DB_NAME` - Database name
4. Click "Deploy" and wait for deployment to complete

---

## 📋 Requirements

See [requirements.txt](requirements.txt) for full list of dependencies:
- pyrofork
- aiohttp
- pymongo
- dnspython
- TgCrypto-pyrofork
- pyromod

---

## 🐛 Troubleshooting

### Bot Not Responding
- Verify `BOT_TOKEN` is correct
- Check internet connection
- Ensure bot is running: `python main.py`

### Join Requests Not Accepted
- Confirm bot has admin permissions in channel
- Verify "accept join request" permission is enabled
- Check logs for error messages

### Database Connection Issues
- Verify `DB_URL` is correct
- Check MongoDB cluster IP whitelist
- Ensure network connectivity

### Flood Wait Errors
- Increase `FLOOD_WAIT` value in config
- Reduce broadcast message frequency
- Optimize database queries

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs via `/report` command
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**OnlyNoco**
- 🔗 [Portfolio](https://onlynoco.vercel.app)
- 💬 [Telegram](https://t.me/OnlyNoco)
- 📦 [GitHub](https://github.com/OnlyNoco)

---

## 📢 Other Stuff

- [Hentai Crisp](https://t.me/+O7PeEMZOAoMzYzVl) - HAnime channel
- [Battle Through the Heavens](https://t.me/HeavenlySubs) - Check this masterpiece

---

## 🗣️ Support

For issues, questions, or suggestions:
- Use the `/report` command in the bot
- Contact [@OnlyNoco](https://t.me/OnlyNoco) on Telegram
- Open an issue on GitHub

---

<div align="center">

**[⬆ Back to Top](#auto-request-accept-bot)**

Made with ❤️ by [OnlyNoco](https://github.com/OnlyNoco)

</div>

---

## 🔄 Upcoming Features
SUGGEST ME!


