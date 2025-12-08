from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_keyboard(user_id):
    buttons = [
        [
            InlineKeyboardButton(text="✅ Evet, Güncelle", callback_data=f"confirm_add_{user_id}"),
            InlineKeyboardButton(text="❌ İptal", callback_data=f"cancel_add_{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)