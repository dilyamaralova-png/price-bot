import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "8882945235:AAGlkOeFY17bxsb_rVxSaTpvDlanQZm2O3w")
ADMIN_ID = 781922474

logging.basicConfig(level=logging.INFO)

CATALOG = {
    "🎵 Spotify": {
        "sections": [
            {
                "label": "Standard",
                "plans": [
                    ("1 месяц", "$2.2"),
                    ("12 месяцев", "$19"),
                ]
            },
            {
                "label": "Platinum",
                "plans": [
                    ("1 месяц", "$5"),
                    ("4.5 месяца", "$20"),
                ]
            },
            {
                "label": "Другие тарифы",
                "plans": [
                    ("Individual", "$2.3"),
                    ("Duo", "$3.2"),
                    ("Family", "$3.5"),
                ]
            }
        ]
    },
    "🎮 Xbox Game Pass": {
        "sections": [
            {
                "label": "Ultimate — любой акк (без подписки)",
                "plans": [
                    ("1 месяц", "$14.8"),
                    ("2 месяца", "$29.6"),
                    ("3 месяца", "$34.3"),
                    ("5 месяцев", "$55.6"),
                    ("7 месяцев", "$67.4"),
                    ("9 месяцев", "$91.1"),
                    ("12+1 мес", "$116"),
                    ("Premium 1м (не Ultimate)", "$9.5"),
                ]
            },
            {
                "label": "Ultimate — новый акк (не было подписок)",
                "plans": [
                    ("3 месяца", "$29.6"),
                    ("5 месяцев", "$45"),
                    ("7 месяцев", "$62.7"),
                    ("9 месяцев", "$80.5"),
                    ("12+1 мес", "$105.3"),
                ]
            },
            {
                "label": "PC — только ПК",
                "plans": [
                    ("12 месяцев", "$68.6"),
                ]
            }
        ]
    },
    "🖼️ Midjourney": {
        "plans": [
            ("Basic", "$9"),
            ("Standard", "$22"),
            ("Pro", "$44"),
        ]
    },
    "🤖 ChatGPT Plus": {
        "sections": [
            {
                "label": "Доступно",
                "plans": [
                    ("По данным/токену", "$16.5"),
                    ("По данным/токену (срочно)", "$18"),
                    ("По ссылке", "$24"),
                ]
            },
            {
                "label": "Временно нет в наличии",
                "plans": [
                    ("Новый акк + почта", "❌ нет"),
                ]
            }
        ]
    },
    "✦ Claude AI": {
        "sections": [
            {
                "label": "Доступно",
                "plans": [
                    ("Pro", "$17"),
                ]
            },
            {
                "label": "Временно нет в наличии",
                "plans": [
                    ("Max ×5", "❌ нет"),
                    ("Max ×20", "❌ нет"),
                ]
            }
        ]
    },
    "⌨️ Cursor AI": {
        "sections": [
            {
                "label": "Новый акк + почта",
                "plans": [
                    ("Pro", "$17"),
                    ("Pro+ и Ultra", "❌ нет"),
                ]
            },
            {
                "label": "Продление",
                "plans": [
                    ("Pro", "$23.5"),
                    ("Pro+", "$66"),
                    ("Ultra", "$218.5"),
                ]
            }
        ]
    },
    "𝕏 Grok AI": {
        "sections": [
            {
                "label": "SuperGrok",
                "plans": [
                    ("Новый акк + почта", "$11"),
                    ("Продление", "$15"),
                ]
            },
            {
                "label": "Другое",
                "plans": [
                    ("CDK", "$17"),
                ]
            }
        ]
    },
    "🎶 Suno AI": {
        "sections": [
            {
                "label": "Индия (UPI)",
                "plans": [
                    ("Pro", "$12"),
                    ("Premier", "$33"),
                ]
            },
            {
                "label": "Другие страны",
                "plans": [
                    ("Pro", "$13"),
                    ("Premier", "$35"),
                ]
            }
        ]
    },
    "🎨 Krea AI": {
        "plans": [
            ("Basic", "$8"),
            ("Pro", "$30.8"),
            ("Max 40k", "$61.6"),
            ("Max 60k", "$92.4"),
            ("Max 80k", "$118.8"),
            ("Max 100k", "$145.2"),
        ]
    },
    "✨ Gamma AI": {
        "plans": [
            ("Plus", "$10.6"),
            ("Pro", "$22"),
        ]
    },
    "🖌️ Freepik AI": {
        "plans": [
            ("Essential", "$12"),
            ("Premium", "$21"),
            ("Premium Plus", "$44"),
        ]
    },
    "🎬 Runway ML": {
        "plans": [
            ("Standard", "$13.2"),
            ("Pro", "$30.8"),
            ("Unlimited", "$83.6"),
        ]
    },
    "🌟 Flair AI": {
        "plans": [
            ("Pro", "$8.8"),
            ("Pro+", "$30.8"),
        ]
    },
    "🎥 Pika Art AI": {
        "plans": [
            ("Standard", "$8.8"),
            ("Pro", "$30.8"),
            ("Fancy", "$83.6"),
        ]
    },
    "🦁 Leonardo AI": {
        "plans": [
            ("Essential", "$14.8"),
            ("Premium", "$34.8"),
            ("Ultimate", "$69"),
        ]
    },
    "🤖 Kling AI": {
        "sections": [
            {
                "label": "Новый аккаунт",
                "plans": [
                    ("Standard", "$8.8"),
                    ("Pro", "$31.5"),
                    ("Premier", "$72.2"),
                    ("Ultra", "$146.8"),
                ]
            },
            {
                "label": "Продление",
                "plans": [
                    ("Standard", "$10.9"),
                    ("Pro", "$39.4"),
                    ("Premier", "$97.2"),
                    ("Ultra", "$183.4"),
                ]
            }
        ]
    },
}

def format_service(name, data):
    lines = [f"<b>{name}</b>\n"]
    if "plans" in data:
        for plan, price in data["plans"]:
            lines.append(f"  {plan} — {price}")
    elif "sections" in data:
        for sec in data["sections"]:
            lines.append(f"\n<i>{sec['label']}</i>")
            for plan, price in sec["plans"]:
                lines.append(f"  {plan} — {price}")
    return "\n".join(lines)

def main_menu_keyboard():
    services = list(CATALOG.keys())
    buttons = []
    row = []
    for i, name in enumerate(services):
        row.append(InlineKeyboardButton(name, callback_data=f"svc:{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("📋 Весь прайс", callback_data="all")])
    buttons.append([InlineKeyboardButton("🛒 Оформить заказ", callback_data="order")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Здесь ты можешь посмотреть цены на подписки и оформить заказ.\n\nВыбери сервис:",
        reply_markup=main_menu_keyboard()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("svc:"):
        name = data[4:]
        svc_data = CATALOG.get(name)
        if not svc_data:
            return
        text = format_service(name, svc_data)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Заказать", callback_data=f"order_svc:{name}")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back")]
        ])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)

    elif data == "all":
        lines = []
        for name, svc_data in CATALOG.items():
            lines.append(format_service(name, svc_data))
            lines.append("")
        text = "\n".join(lines)
        if len(text) > 4000:
            parts = []
            current = ""
            for line in lines:
                if len(current) + len(line) > 3800:
                    parts.append(current)
                    current = line + "\n"
                else:
                    current += line + "\n"
            if current:
                parts.append(current)
            await query.edit_message_text(
                parts[0], parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back")]])
            )
            for part in parts[1:]:
                await query.message.reply_text(part, parse_mode="HTML")
        else:
            await query.edit_message_text(
                text, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back")]])
            )

    elif data == "order" or data.startswith("order_svc:"):
        svc_name = data[10:] if data.startswith("order_svc:") else ""
        hint = f" ({svc_name})" if svc_name else ""
        context.user_data["ordering"] = True
        context.user_data["order_svc"] = svc_name
        await query.edit_message_text(
            f"📝 Оформление заказа{hint}\n\nНапиши что именно хочешь заказать — сервис, тариф, период. Я передам заявку.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Отмена", callback_data="back")]])
        )

    elif data == "back":
        await query.edit_message_text(
            "Выбери сервис:",
            reply_markup=main_menu_keyboard()
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("ordering"):
        user = update.effective_user
        svc = context.user_data.get("order_svc", "")
        text = update.message.text
        username = f"@{user.username}" if user.username else f"id:{user.id}"
        name = user.full_name or ""

        order_text = (
            f"🛒 <b>Новый заказ!</b>\n\n"
            f"👤 {name} {username}\n"
            + (f"📦 Сервис: {svc}\n" if svc else "")
            + f"📝 Сообщение:\n{text}"
        )

        await context.bot.send_message(ADMIN_ID, order_text, parse_mode="HTML")
        await update.message.reply_text(
            "✅ Заявка отправлена! Скоро свяжусь с тобой.",
            reply_markup=main_menu_keyboard()
        )
        context.user_data["ordering"] = False
        context.user_data["order_svc"] = ""
    else:
        await update.message.reply_text(
            "Выбери сервис из меню:",
            reply_markup=main_menu_keyboard()
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
