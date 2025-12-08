from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from database.db import db
from handlers.admin import AnimeStates, refresh_list

router = Router()

@router.callback_query(AnimeStates.waiting_for_overwrite, F.data.startswith("confirm_add_"))
async def confirm_overwrite(callback: types.CallbackQuery, state: FSMContext):
    owner_id = int(callback.data.split("_")[-1])
    if callback.from_user.id != owner_id:
        await callback.answer("⚠️ Bu işlem size ait değil!", show_alert=True)
        return

    data = await state.get_data()
    db.force_add_anime(data['title'], data['url'], callback.from_user.id)
    await callback.message.edit_text(f"✅ **{data['title']}** güncellendi.")
    await state.clear()
    await refresh_list(callback.message)

@router.callback_query(AnimeStates.waiting_for_overwrite, F.data.startswith("cancel_add_"))
async def cancel_overwrite(callback: types.CallbackQuery, state: FSMContext):
    owner_id = int(callback.data.split("_")[-1])
    if callback.from_user.id != owner_id:
        await callback.answer("⚠️ Bu işlem size ait değil!", show_alert=True)
        return

    await callback.message.edit_text("❌ İşlem iptal edildi.")
    await state.clear()