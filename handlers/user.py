from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db import db

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Hoş geldiniz! Anime aramak için /ara komutunu kullanabilir veya inline modda beni etiketleyebilirsiniz.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "🤖 **Bot Komutları**\n\n"
        "/ara <kelime> - Anime arar\n"
        "@botkullaniciadi <kelime> - Inline arama yapar"
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