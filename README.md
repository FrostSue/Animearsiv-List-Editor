# 🤖 Advanced Telegram Anime Manager Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blueviolet?style=for-the-badge&logo=telegram)
![Flask](https://img.shields.io/badge/Flask-Web_Panel-black?style=for-the-badge&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

A robust, modular, and professional Telegram bot designed to manage, store, and serve anime lists. Built with **Python**, **aiogram**, and **Flask**, utilizing a JSON-based database with automatic backup systems.

---

## 🌟 Features

### 🛡️ Admin System
- **Dynamic Admin Management:** The bot owner can add/remove admins via commands.
- **Secure Handling:** Only admins can add content, import lists, or manage backups.
- **Import Capabilities:** Import anime links in bulk by replying to a message containing links.
- **Duplicate Detection:** Automatically detects duplicate titles or URLs and asks for overwrite confirmation.

### 🔍 User Features
- **Global Search:** Search the anime database via commands.
- **Inline Mode:** Search and share anime directly in any chat using `@BotUsername query`.
- **Smart Pagination:** Automatically splits long lists into multiple messages to respect Telegram limits.

### ⚙️ System & Web Panel
- **Web Interface:** A Flask-based web panel to view the list, delete entries, and download the JSON database.
- **Auto-Backups:** Daily automatic backups of the database + Manual backup command.
- **Dockerized:** Fully containerized for easy deployment.
- **JSON Database:** Lightweight, portable, and human-readable data storage.

---

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.10+ or Docker
- A Telegram Bot Token (from @BotFather)

---

## Option 1: **Docker (Recommended)**

### 1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME
````

### 2. Configure Environment

Create a `.env` file in the root directory:

```
BOT_TOKEN=your_telegram_bot_token
OWNER_ID=your_telegram_user_id
WEB_PORT=5000
```

### 3. Build and Run:

```bash
docker-compose up --build -d
```

---

## Option 2: **Local Run**

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the bot:

```bash
python bot.py
```

---

## 🎮 Usage & Commands

### 👑 Admin Commands

| Command                         | Description                                           |                                  |
| ------------------------------- | ----------------------------------------------------- | -------------------------------- |
| `/ekle <Name>                   | <Link>`                                               | Add a new anime to the database. |
| `/yedekle`                      | Create an immediate manual backup.                    |                                  |
| `/addadmin <id>` *(Owner Only)* | Promote a user to admin.                              |                                  |
| `/deladmin <id>` *(Owner Only)* | Demote an admin.                                      |                                  |
| **Reply “import”**              | Reply to any message containing links to bulk import. |                                  |

### 👤 User Commands

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `/start`           | Start the bot and see the welcome message. |
| `/help`            | View available commands.                   |
| `/ara <query>`     | Search for an anime in the database.       |
| `@BotName <query>` | Use inline search in any chat.             |

---

## 📂 Project Structure

```plaintext
├── backups/           # Auto-generated backups
├── database/          # JSON Database engine
├── handlers/          # Bot logic (Admin, User, Inline)
├── utils/             # Helpers & Keyboard builders
├── web/               # Flask Web Panel
├── bot.py             # Entry point
├── docker-compose.yml # Docker configuration
└── .env               # Secrets
```

---

## 🌐 Web Panel Access

The web panel runs on port **5000** by default.

* Local: `http://localhost:5000`
* Server: `http://YOUR_SERVER_IP:5000`

---

## 📄 License

This project is open-source and available under the **MIT License**.
