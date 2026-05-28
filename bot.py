import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

CATALOG = {
    "spotify": ("🎵 Spotify", [
        ("Standard 1 мес", "$2.2"),
        ("Standard 12 мес", "$19"),
        ("Platinum 1 мес", "$5"),
        ("Platinum 4.5 мес", "$20"),
        ("Individual", "$2.3"),
        ("Duo", "$3.2"),
        ("Family", "$3.5"),
    ]),
    "midjourney": ("🖼️ Midjourney", [
        ("Basic", "$9"),
        ("Standard", "$22"),
        ("Pro", "$44"),
    ]),
    "chatgpt": ("🤖 ChatGPT Plus", [
        ("По данным/токену", "$16.5"),
        ("Новый акк + почта", "❌ нет"),
        ("По ссылке", "$24"),
    ]),
    "claude": ("✦ Claude AI", [
        ("Pro", "$17"),
        ("Max ×5", "❌ нет"),
        ("Max ×20", "❌ нет"),
    ]),
    "cursor": ("⌨️ Cursor AI", [
        ("Pro новый акк+почта", "$17"),
        ("Pro продление", "$23.5"),
        ("Pro+ новый акк+почта", "❌ нет"),
        ("Pro+ продление", "$66"),
        ("Ultra новый акк+почта", "❌ нет"),
        ("Ultra продление", "$218.5"),
    ]),
    "grok": ("𝕏 Grok AI", [
        ("SuperGrok новый акк+почта", "$11"),
        ("SuperGrok продление", "$15"),
        ("CDK", "$17"),
    ]),
    "suno": ("🎶 Suno AI", [
        ("Pro (Индия UPI)", "$12"),
        ("Premier (Индия UPI)", "$33"),
        ("Pro (другие страны)", "$13"),
        ("Premier (другие страны)", "$35"),
    ]),
    "krea": ("🎨 Krea AI", [
        ("Basic", "$8"),
        ("Pro", "$30.8"),
        ("Max 40k", "$61.6"),
        ("Max 60k", "$92.4"),
        ("Max 80k", "$118.8"),
        ("Max 100k", "$145.2"),
    ]),
    "gamma": ("✨ Gamma AI", [
        ("Plus", "$10.6"),
        ("Pro", "$22"),
    ]),
    "freepik": ("🖌️ Freepik AI", [
        ("Essential", "$12"),
        ("Premium", "$21"),
        ("Premium Plus", "$44"),
    ]),
    "runway": ("🎬 Runway ML", [
        ("Standard", "$13.2"),
        ("Pro", "$30.8"),
        ("Unlimited", "$83.6"),
    ]),
    "flair": ("🌟 Flair AI", [
        ("Pro", "$8.8"),
        ("Pro+", "$30.8"),
    ]),
    "pika": ("🎥 Pika Art AI", [
        ("Standard", "$8.8"),
        ("Pro", "$30.8"),
        ("Fancy", "$83.6"),
    ]),
    "leonardo": ("🦁 Leonardo AI", [
        ("Essential", "$14.8"),
        ("Premium", "$34.8"),
        ("Ultimate", "$69"),
    ]),
    "kling": ("🤖 Kling AI", [
        ("Standard новый", "$8.8"),
        ("Standard продление", "$10.9"),
        ("Pro новый", "$31.5"),
        ("Pro продление", "$39.4"),
        ("Premier новый", "$72.2"),
        ("Premier продление", "$97.2"),
        ("Ultra новый", "$146.8"),
        ("Ultra продление", "$183.4"),
    ]),
    "xbox": ("🎮 Xbox Game Pass", [
        ("Ultimate 1м (любой акк)", "$14.8"),
        ("Ultimate 2м (любой акк)", "$29.6"),
        ("Ultimate 3м (любой акк)", "$34.3"),
        ("Ultimate 5м (любой акк)", "$55.6"),
        ("Ultimate 7м (любой акк)", "$67.4"),
        ("Ultimate 9м (любой акк)", "$91.1"),
        ("Ultimate 12+1м (любой акк)", "$116"),
        ("Premium 1м (любой акк)", "$9.5"),
        ("Ultimate 3м (новый акк)", "$29.6"),
        ("Ultimate 5м (новый акк)", "$45"),
        ("Ultimate 7м (новый акк)", "$62.7"),
        ("Ultimate 9м (новый акк)", "$80.5"),
        ("Ultimate 12+1м (новый акк)", "$105.3"),
        ("PC 12м (только ПК)", "$68.6"),
    ]),
}


def main_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(v[0], callback_data=f"svc:{k}") for k, v in CATALOG.items()]
    kb.add(*buttons)
    kb.add(InlineKeyboardButton("📋 Весь прайс", callback_data="all"))
    return kb


def back_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return kb


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Здесь можно посмотреть цены на подписки.\n\nВыбери сервис:",
        reply_markup=main_keyboard()
    )


@bot.callback_query_handler(func=lambda c: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    data = call.data

    if data.startswith("svc:"):
        key = data[4:]
        name, plans = CATALOG[key]
        lines = [f"<b>{name}</b>\n"]
        for plan, price in plans:
            lines.append(f"  {plan} — {price}")
        bot.edit_message_text(
            "\n".join(lines),
            chat_id, call.message.message_id,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )

    elif data == "all":
        lines = []
        for key, (name, plans) in CATALOG.items():
            lines.append(f"<b>{name}</b>")
            for plan, price in plans:
                lines.append(f"  {plan} — {price}")
            lines.append("")
        text = "\n".join(lines)
        chunks = []
        current = ""
        for line in text.split("\n"):
            if len(current) + len(line) + 1 > 3800:
                chunks.append(current)
                current = line + "\n"
            else:
                current += line + "\n"
        if current:
            chunks.append(current)
        bot.edit_message_text(
            chunks[0], chat_id, call.message.message_id,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
        for chunk in chunks[1:]:
            bot.send_message(chat_id, chunk, parse_mode="HTML")

    elif data == "back":
        bot.edit_message_text(
            "Выбери сервис:",
            chat_id, call.message.message_id,
            reply_markup=main_keyboard()
        )

    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.send_message(message.chat.id, "Выбери сервис:", reply_markup=main_keyboard())


print("Бот запущен...")
bot.infinity_polling()
