import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db import db

router = Router()
OWNER_ID = int(os.getenv("OWNER_ID", 0))

def is_admin(user_id):
    return user_id == OWNER_ID or user_id in db.get_admins()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Hoş geldiniz! Anime aramak için /ara komutunu kullanabilir veya inline modda beni etiketleyebilirsiniz.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "🤖 **Kullanıcı Komutları**\n"
        "--------------------------\n"
        "• `/ara <kelime>` : Anime arar\n"
        "• `@BotKullaniciAdi <kelime>` : Sohbetlerde inline arama\n"
    )

    if is_admin(message.from_user.id):
        text += (
            "\n👮‍♂️ **Admin Komutları**\n"
            "--------------------------\n"
            "• `/ekle Ad | Link` : Yeni anime ekler\n"
            "• `/yedekle` : Veritabanını yedekler\n"
            "• `/addadmin <id>` : Yeni admin ekler (Sadece Owner)\n"
            "• `/deladmin <id>` : Admin siler (Sadece Owner)\n"
            "• **Import** : Linkli mesaja yanıt olarak 'import' yazın."
        )

    await message.answer(text, parse_mode="Markdown")

@router.message(Command("ara"))
async def cmd_search(message: Message):
    query = message.text.replace("/ara", "").strip().lower()
    if not query:
        await message.answer("🔍 Lütfen aranacak kelimeyi yazın.\nÖrnek: `/ara Naruto`", parse_mode="Markdown")
        return

    data = db.load()
    results = [a for a in data["anime_list"] if query in a["title"].lower()]

    if not results:
        await message.answer("❌ Sonuç bulunamadı.")
        return

    text = f"🔍 **Arama Sonuçları: '{query}'**\n\n"
    for anime in results:
        text += f"• [{anime['title']}]({anime['url']})\n"

    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)