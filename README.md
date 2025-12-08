# 🤖 Advanced Telegram Anime Manager Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blueviolet?style=for-the-badge&logo=telegram)
![Flask](https://img.shields.io/badge/Flask-Web_Panel-black?style=for-the-badge&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![Cloudflare](https://img.shields.io/badge/Cloudflare-Tunnel-orange?style=for-the-badge&logo=cloudflare)

A robust, modular, and professional Telegram bot designed to manage, store, and serve anime lists. Features a **secure Web Admin Panel** accessible via **Cloudflare Tunnel** without port forwarding, advanced **JSON Database**, and **Smart Import** capabilities.

## 🌟 Key Features

### 🛡️ Admin & Web System
- **Secure Web Panel:** Flask-based admin panel with login protection (hashed passwords).
- **Cloudflare Tunnel:** Automatically creates a secure HTTPS link to the web panel on startup. No port forwarding required.
- **Dynamic Access:** Admins can generate the current web link via the `/site` command.
- **Web CRUD:** Edit titles, URLs, delete entries, and manage web admins directly from the browser.
- **JSON Management:** Download the full database backup instantly.

### 🤖 Bot Capabilities
- **Smart Import:** Simply **forward** a message with links to the bot to import anime automatically.
- **Manual Publish:** Changes are staged and only published to the channel/group when you use `/yayinla`.
- **Inline Search:** Users can search and share anime in any chat using `@BotName query`.
- **Duplicate Protection:** Prevents duplicate entries and prompts for overwrite confirmation.

### ⚙️ System
- **Dockerized:** Fully containerized with `cloudflared` integrated.
- **Auto-Backups:** Daily automatic backups + Manual backup command.
- **Data Integrity:** Auto-sanitization of titles (fixes markdown/newline errors).

---

## 🚀 Installation & Setup

### Prerequisites
- Docker & Docker Compose
- A Telegram Bot Token (from @BotFather)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME
```

### 2. Configure Environment

Create a `.env` file in the root directory. This file is **crucial** for security and initial setup.

```env
BOT_TOKEN=your_telegram_bot_token
OWNER_ID=your_telegram_user_id
WEB_PORT=5000

# Initial Web Admin Credentials (Used to create the first admin)
DEFAULT_WEB_USER=AdminUser
DEFAULT_WEB_PASS=StrongPassword123!
```

### 3. Build and Run

```bash
docker-compose up --build -d
```

---

## 🎮 Usage & Commands

### 👑 Bot Owner Commands

| Command | Description |
|--------|-------------|
| `/addadmin <id>` | Promote a Telegram user to Bot Admin. |
| `/deladmin <id>` | Demote a Bot Admin. |
| `/siteadmin <user> <pass>` | Create a new **Web Panel** admin account. |

### 👮‍♂️ Admin Commands

| Command | Description |
|--------|-------------|
| `/site` | **Get the secure Cloudflare link** to access the Web Panel. |
| `/yayinla` | Publish/Update the anime list in the chat. |
| `/ekle <Name> \| <Link>` | Manually add a single anime. |
| `/yedekle` | Create an immediate database backup. |
| `/import` | (Reply) Import links from a replied message. |
| **Forward Message** | Forward any message with links to auto-import. |

### 👤 User Commands

| Command | Description |
|--------|-------------|
| `/start` | Start the bot. |
| `/help` | View available commands. |
| `/ara <query>` | Search for an anime. |
| `@BotName <query>` | Use inline search in any chat. |

---

## 🌐 Web Panel Guide

1. **Get Link:** Send `/site` to the bot.  
2. **Login:** Use the credentials defined in your `.env` file (or created via `/siteadmin`).  
3. **Dashboard:**  
   - **Edit** titles or update broken links.  
   - **Delete** anime entries.  
   - **Settings:** Add new web administrators.  
   - **Download:** Get the `data.json` file.  

---

## 📂 Project Structure

```text
├── backups/           # Auto-generated backups
├── database/          # JSON Database & Logic
├── handlers/          # Bot Command Handlers
│   ├── admin.py       # Admin & Smart Import logic
│   ├── user.py        # User commands
│   └── inline.py      # Inline search logic
├── utils/             # Helpers & Tunnel Manager
│   ├── tunnel.py      # Cloudflare process manager
│   └── ...
├── web/               # Flask Application
│   ├── templates/     # HTML Files (Login, Edit, Index)
│   └── panel.py       # Web Server Logic
├── bot.py             # Main Entry Point
├── Dockerfile         # Custom image with Cloudflared
└── docker-compose.yml # Service orchestration
```

## 📄 License

This project is open-source and available under the MIT License.
