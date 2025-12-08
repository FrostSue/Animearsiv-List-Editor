import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import admin, user, common, inline
from database.db import db
from web.panel import start_web_server

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

logging.basicConfig(level=logging.INFO)

async def scheduled_backup():
    filename = db.create_backup()
    logging.info(f"Otomatik yedek alındı: {filename}")

async def set_commands(bot: Bot):
    user_commands = [
        BotCommand(command="start", description="Botu başlat"),
        BotCommand(command="help", description="Yardım menüsü"),
        BotCommand(command="ara", description="Anime ara"),
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    admin_commands = user_commands + [
        BotCommand(command="ekle", description="Yeni anime ekle"),
        BotCommand(command="yedekle", description="Manuel yedek al"),
        BotCommand(command="addadmin", description="Admin ekle (Owner)"),
        BotCommand(command="deladmin", description="Admin sil (Owner)")
    ]
    
    admins = db.get_admins()
    admins.append(OWNER_ID)
    
    for admin_id in set(admins):
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except:
            pass

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(inline.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_backup, 'interval', hours=24)
    scheduler.start()

    start_web_server()
    
    await set_commands(bot)
    
    print("🤖 Bot ve Web Panel çalışıyor...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot durduruldu.")