from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

button1 = InlineKeyboardButton(
    text="🚕 Farg'ona → Yaypan",
    callback_data="fargona_yaypan"
)
button2 = InlineKeyboardButton(
    text="🚕 Yaypan → Farg'ona",
    callback_data="yaypan_fargona"
)
button3 = InlineKeyboardButton(
    text="🚕 Yaypan → Yakatut",
    callback_data="yaypan_yakatut"
)
button4 = InlineKeyboardButton(
    text="🚕 Yakatut → Yaypan",
    callback_data="yakatut_yaypan"
)
cancel_button = KeyboardButton(
    text="Bekor qilish",
    callback_data="cancel_order"
)
button_order = KeyboardButton(text="🚖 Buyurtma berish")
times = []
count = 4
for i in range(1, 7):
    row = []
    for j in range(1, 4):
        row.append(InlineKeyboardButton(text=f"{count}:00-{count+1}:00", callback_data=f"t_{count}"))
        count += 1
    times.append(row)
times.append([InlineKeyboardButton(text="Aniq emas", callback_data=f"t_different")])

person_1 = InlineKeyboardButton(
    text="1",
    callback_data="p_1"
)
person_2 = InlineKeyboardButton(
    text="2",
    callback_data="p_2"
)
person_3 = InlineKeyboardButton(
    text="3",
    callback_data="p_3"
)
person_4 = InlineKeyboardButton(
    text="4",
    callback_data="p_4"
)
person_mail = InlineKeyboardButton(
    text="Pochta",
    callback_data="p_mail"
)
gender_male = InlineKeyboardButton(
    text="Erkak",
    callback_data="g_male"
)
gender_female = InlineKeyboardButton(
    text="Ayol",
    callback_data="g_female"
)
gender_union = InlineKeyboardButton(
    text="Ikkisi ham",
    callback_data="g_other"
)
confirm_yes = InlineKeyboardButton(
    text="✅ Ha",
    callback_data="c_yes"
)
confirm_no = InlineKeyboardButton(
    text="🚫 Yo'q",
    callback_data="c_no"
)
menu = ReplyKeyboardMarkup(keyboard=[[button_order]], resize_keyboard=True)
direction_inline = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2], [button3], [button4]])
cancel_order_button = ReplyKeyboardMarkup(keyboard=[[cancel_button]], resize_keyboard=True)
time_buttons = InlineKeyboardMarkup(inline_keyboard=times)
person_buttons = InlineKeyboardMarkup(inline_keyboard=[[person_1, person_2], [person_3, person_4], [person_mail]])
gender_buttons = InlineKeyboardMarkup(inline_keyboard=[[gender_female, gender_male], [gender_union]])
confirm_buttons = InlineKeyboardMarkup(inline_keyboard=[[confirm_yes, confirm_no]])