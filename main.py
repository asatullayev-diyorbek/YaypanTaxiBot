import asyncio
import os
import re

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, ChatMemberAdministrator, \
    ChatMemberOwner
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from database import (
    save_phone_number, new_order, get_user,
    delete_order, get_order, update_order, get_group, add_group
)
# tugmalar
from buttons import (
    direction_inline, cancel_order_button,
    menu, time_buttons, person_buttons,
    gender_buttons, confirm_buttons
)
from models import directions
# .env faylini o'qish
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

DATABASE_URL = os.getenv('DATABASE_URL')  # Ma'lumotlar bazasi ulanishi

bot = Bot(token=str(API_TOKEN))
dp = Dispatcher()

Base = declarative_base()

# SQLAlchemy database setup
engine = create_engine(DATABASE_URL, echo=True, future=True)  # "future=True" qo'shib qo'yish kerak
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

# Telefon raqamni yuborish uchun tugma
phone_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

async def send_welcome(message: Message):
    await message.answer("*Kerakli bo'limni tanlang:*", reply_markup=menu, parse_mode="Markdown")

async def get_order_id(text: str):
    match = re.search(r"ID-(\d+)", text)
    if match:
        return int(match.group(1))
    return None

async def delete_message(message: Message):
    try:
        await message.delete()
    except:
        await message.reply("*Ushbu xabar eskirgan!*", parse_mode="Markdown")

@dp.message(F.contact)
async def save_contact(message: Message):
    user = get_user(message.chat.id)
    if not user:
        chat_id = message.chat.id
        first_name = message.chat.first_name if message.chat.first_name else ''
        last_name = message.chat.last_name if message.chat.last_name else ''
        full_name = first_name + ' ' + last_name
        phone_number = message.contact.phone_number
        # Yordamchi funksiyani chaqirish
        user = save_phone_number(chat_id, full_name, phone_number)
        await message.answer(
            f"✅ Ma'lumotlaringiz qabul qilindi!\n\n"
            f"👤 <b>F.I.O:</b> {user.full_name}\n"
            f"📞 <b>Telefon raqam:</b> {user.phone_number}",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "⚠️ <b>Diqqat!</b>\n\n"
            "📞 Raqamingiz avvalroq saqlangan.",
            parse_mode="HTML"
        )
    await send_welcome(message)


@dp.message(Command("start"))
async def start_command(message: Message):
    chat_id = message.chat.id
    if message.chat.type == "private":
        user = get_user(chat_id)
        if user:
            # Agar foydalanuvchi baza ichida mavjud bo'lsa, buyurtma berish uchun tugmani chiqar
            # button_order = KeyboardButton(text="🚖 Buyurtma berish")
            # menu = ReplyKeyboardMarkup(keyboard=[[button_order]], resize_keyboard=True)
            await message.answer("*Kerakli bo'limni tanlang:*", reply_markup=menu, parse_mode="Markdown")
        else:
            # Agar foydalanuvchi baza ichida mavjud emas bo'lsa, telefon raqami so'rash kerak
            await message.answer(
                f"<b>Assalomu alaykum! {message.chat.full_name}</b>\n\n"
                "📱 <i>Iltimos, raqamingizni yuboring:</i>",
                reply_markup=phone_button,
                parse_mode="HTML"
            )

@dp.message(Command("activate"))
async def activate_group(message: Message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        chat_title = message.chat.title
        group = get_group()

        bot_member = await message.bot.get_chat_member(chat_id, message.bot.id)
        if not isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner)):
            await message.answer(
                "⚠️ <b>Diqqat!</b>\n\n"
                "Bot ushbu guruhda <b>administrator</b> emas. "
                "🔑 <i>Guruhni aktivatsiya qilish uchun botni administrator qiling.</i>",
                parse_mode="HTML"
            )
            return

        if not group:
            add_group(chat_id, chat_title)
            await message.answer(
                f"✅ <b>Guruh muvaffaqiyatli activate qilindi!</b>\n\n"
                f"📌 <b>Guruh nomi:</b> <i>{chat_title}</i>\n"
                f"🆔 <b>Guruh ID:</b> <code>{chat_id}</code>",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"⚠️ <b>Botga guruh allaqachon biriktirilgan!</b>\n\n"
                f"📌 <b>Guruh nomi:</b> <i>{group.group_name}</i>\n"
                f"🆔 <b>Guruh ID:</b> <code>{group.chat_id}</code>",
                parse_mode="HTML"
            )

@dp.message(Command("deactivate"))
async def deactivate_group(message: Message):
    if message.chat.type in ["group", "supergroup"]:
        chat_id = message.chat.id
        group = get_group()

        if not group or chat_id != group.chat_id:
            await message.answer(
                f"⚠️ <b>Bot ushbu guruhga biriktirilmagan!</b>",
                parse_mode="HTML"
            )
            return
        else:
            group.delete()

            await message.answer(
                f"✅ <b>Guruh muvaffaqiyatli deaktivatsiya qilindi!</b>\n\n"
                f"🆔 <b>Guruh ID:</b> <code>{chat_id}</code>",
                parse_mode="HTML"
            )
            return

# @dp.message(F.text == "Bekor qilish")
async def cancel_order(message: Message):
    user = get_user(message.chat.id)
    if not user:
        await message.answer("🔄 Iltimos, /start buyrug'ini yuboring!", parse_mode="Markdown")
        return
    order = get_order(user)
    if not order:
        await message.answer("❌ Sizda buyurtma mavjud emas!", parse_mode="Markdown")
        return
    delete_order(order)
    await message.reply(
        "✅ Buyurtma muvaffaqiyatli bekor qilindi!\n\n"
        "📋 Agar yangi buyurtma bermoqchi bo'lsangiz, menyudan kerakli bo'limni tanlang.",
        reply_markup=menu
    )


# Buyurtma berishni boshlash tugmasi
# @dp.message(F.text == "Buyurtma berish")
async def _order_create(message: Message):
    user = get_user(message.chat.id)
    if not user:
        await message.answer("🔄 Iltimos, /start buyrug'ini yuboring!", parse_mode="Markdown")
        return

    order = new_order(user)
    await message.reply(
        "🚕 Buyurtma berishni boshlaymiz!\nIltimos so'ralgan ma'lumotlarni kiriting",
        reply_markup=cancel_order_button
    )
    await message.answer(
        f"{order.info()}\n\n📍 *Yo'nalishni tanlang:*",
        reply_markup=direction_inline,
        parse_mode="Markdown"
    )
    # await delete_message(message)


@dp.callback_query()
async def handle_direction_selection(callback_query: CallbackQuery):
    select_option = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    # await callback_query.message.answer(f"Yo'nalish: {select_option}")

    user = get_user(chat_id)
    if not user:
        await callback_query.message.answer("🔄 Iltimos, /start buyrug'ini yuboring!", parse_mode="Markdown")
        return
    order = get_order(user)
    order_id = await get_order_id(callback_query.message.text)
    # await callback_query.message.reply(f"Buyurtma ID: {order_id}")
    if order_id != order.id:
        await callback_query.message.reply(
            "⚠️ *Bu xabar eskirgan!*",
            reply_markup=menu,
            parse_mode="Markdown"
        )
        return

    if not order or order.extra_column == 0:
        await callback_query.message.answer(
            "🚖 *Buyurtma berishni boshlash uchun* **'Buyurtma berish'** tugmasini bosing!",
            reply_markup=menu,
            parse_mode="Markdown"
        )
        return

    if select_option in directions.keys():
        # Order modeliga yo'nalishni saqlash
        if order.extra_column == 1:
            # order.direction = select_option
            # order.extra_column = 2
            order = update_order(order, direction=select_option, extra_column=2)
            # session.commit()
            await callback_query.message.edit_text(
                f"{order.info()}\n\n⌛ *Ketish vaqtni tanlang:*",
                reply_markup=time_buttons,
                parse_mode="Markdown"
            )
        else:
            await callback_query.answer(
                "⚠️ Kerakli tugmani bosing yoki buyurtma berishni qaytadan boshlang."
            )
            await delete_message(callback_query.message)

    if select_option.startswith("t_"):
        time_option = select_option.split("_")[1]
        if order.extra_column == 2:
            # order.leave_time = time_option
            # order.extra_column = 3
            # session.commit()
            order = update_order(order, leave_time=time_option, extra_column=3)
            await callback_query.message.edit_text(
                f"{order.info()}\n\nYo'lovchilar soni: ",
                reply_markup=person_buttons,
                parse_mode="Markdown"
            )

        else:
            await callback_query.answer(
                "⚠️ Kerakli tugmani bosing yoki buyurtma berishni qaytadan boshlang."
            )
            await delete_message(callback_query.message)

    if select_option.startswith("p_"):
        select_gender = select_option.split("_")[1]
        if order.extra_column == 3:
            # order.person_count = select_person
            # order.extra_column = 4
            # session.commit()
            order = update_order(order, person_count=select_gender, extra_column=4)
            if order.person_count == "mail":
                order = update_order(order, extra_column=5)
                await callback_query.message.edit_text(
                    f"{order.info()}\n\nHaydovchi uchun izoh yozing:\n`Bu yerga bog'lanish uchun qo'shimcha raqam yoki manzilingizni to'liqroq kirishitishgiz mumkin. Masalan: 901234567 | Yaypan, Asmo supermarketi oldida.`",
                    parse_mode="Markdown"
                )
                return
            await callback_query.message.edit_text(
                f"{order.info()}\n\nYo'lovchilar jinsi:",
                reply_markup=gender_buttons,
                parse_mode="Markdown"
            )
        else:
            await callback_query.answer(
                "⚠️ Kerakli tugmani bosing yoki buyurtma berishni qaytadan boshlang."
            )
            await delete_message(callback_query.message)

    if select_option.startswith("g_"):
        select_gender = select_option.split("_")[1]
        if order.extra_column == 4:
            # order.person_count = select_person
            # order.extra_column = 4
            # session.commit()
            order = update_order(order, gender=select_gender, extra_column=5)
            # select_time = f"{order.leave_time}:00 - {int(order.leave_time)+1}:00" if order.leave_time.isdigit() else "Boshqa vaqt"
            # person_count = f"{order.person_count}" if order.person_count.isdigit() else "Pochta"
            await callback_query.message.edit_text(
                f"{order.info()}\n\nHaydovchi uchun izoh yozing:\n`Bu yerga bog'lanish uchun qo'shimcha raqam yoki manzilingizni to'liqroq kirishitishgiz mumkin. Masalan: 901234567 | Yaypan, Asmo supermarketi oldida.`",
                parse_mode="Markdown"
            )
        else:
            await callback_query.answer(
                "⚠️ Kerakli tugmani bosing yoki buyurtma berishni qaytadan boshlang."
            )
            await delete_message(callback_query.message)

    if select_option.startswith("c_"):
        select_confirm = select_option.split("_")[1]
        if order.extra_column == 9:
            # order.comment = select_comment
            # order.extra_column = 10
            # session.commit()
            if select_confirm == "yes":
                order = update_order(order, extra_column=10)
                await callback_query.message.answer(
                    f"🗓✅ Buyurtmangiz qabul qilindi . \nTez orada siz bilan bog'lanamiz!\n\n{order.info()}",
                    reply_markup=menu,
                    parse_mode="Markdown"
                )
                group = get_group()
                if group:
                    await bot.send_message(chat_id=group.chat_id, text=f"{order.info_for_group(user=user)}", parse_mode="HTML")
            else:
                await cancel_order(message=callback_query.message)
                # await callback_query.message.answer(f"ID-{order.id} Buyurtma bekor qilindi!")
            await delete_message(callback_query.message)
        else:
            await callback_query.answer(
                "⚠️ Kerakli tugmani bosing yoki buyurtma berishni qaytadan boshlang."
            )
            await delete_message(callback_query.message)

    session.commit()
    return

@dp.message()
async def handle_message(message: Message):
    if message.chat.type != "private":
        return
    text = message.text
    if text == "🚖 Buyurtma berish":
        await _order_create(message)
        return
    if text == "Bekor qilish":
        await cancel_order(message)
        return

    chat_id = message.chat.id

    user = get_user(chat_id)
    if not user:
        await message.answer("🔄 Iltimos, /start buyrug'ini yuboring!", parse_mode="Markdown")
        return
    order = get_order(user)
    user_message = message.text

    if order and order.extra_column == 5:
        if len(user_message) > 300:
            await message.reply("Izoh maksimal 300 ta harfdan bo'lishi mumkin!")
            return
        update_order(order, comment=user_message, extra_column=9)
        await message.reply(f"{order.info()}\n\nBuyurtma ma'lumotlarini tasdiqlaysizmi?",
                            reply_markup=confirm_buttons,
                            parse_mode="Markdown"
                            )
        return

    await message.reply("Foydalanuvchidan bunday xabar kutilmayapti")

async def main():
    print("Bot ishga tushdi...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
