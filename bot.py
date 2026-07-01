import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "8882945235:AAGlkOeFY17bxsb_rVxSaTpvDlanQZm2O3w")
ADMIN_IDS = [781922474]  # добавляй сюда ID через запятую

logging.basicConfig(level=logging.INFO)

PRICES_FILE = "prices.json"

DEFAULT_CATALOG = {
    "🎵 Spotify": {
        "sections": [
            {
                "label": "Standard",
                "plans": [
                    ["1 месяц", "$2.2"],
                    ["12 месяцев", "$19"],
                ]
            },
            {
                "label": "Platinum",
                "plans": [
                    ["1 месяц", "$5"],
                    ["4.5 месяца", "$20"],
                ]
            },
            {
                "label": "Другие тарифы",
                "plans": [
                    ["Individual", "$2.3"],
                    ["Duo", "$3.2"],
                    ["Family", "$3.5"],
                ]
            }
        ]
    },
    "🎮 Xbox Game Pass": {
        "sections": [
            {
                "label": "Ultimate — любой акк (без подписки)",
                "plans": [
                    ["1 месяц", "$14.8"],
                    ["2 месяца", "$29.6"],
                    ["3 месяца", "$34.3"],
                    ["5 месяцев", "$55.6"],
                    ["7 месяцев", "$67.4"],
                    ["9 месяцев", "$91.1"],
                    ["12+1 мес", "$116"],
                    ["Premium 1м (не Ultimate)", "$9.5"],
                ]
            },
            {
                "label": "Ultimate — новый акк (не было подписок)",
                "plans": [
                    ["3 месяца", "$29.6"],
                    ["5 месяцев", "$45"],
                    ["7 месяцев", "$62.7"],
                    ["9 месяцев", "$80.5"],
                    ["12+1 мес", "$105.3"],
                ]
            },
            {
                "label": "PC — только ПК",
                "plans": [
                    ["12 месяцев", "$68.6"],
                ]
            }
        ]
    },
    "🖼️ Midjourney": {
        "plans": [
            ["Basic", "$9"],
            ["Standard", "$22"],
            ["Pro", "$44"],
        ]
    },
    "🤖 ChatGPT Plus": {
        "sections": [
            {
                "label": "Доступно",
                "plans": [
                    ["По данным/токену", "$16.5"],
                    ["По данным/токену (срочно)", "$18"],
                    ["По ссылке", "$24"],
                ]
            },
            {
                "label": "Временно нет в наличии",
                "plans": [
                    ["Новый акк + почта", "❌ нет"],
                ]
            }
        ]
    },
    "✦ Claude AI": {
        "sections": [
            {
                "label": "Доступно",
                "plans": [
                    ["Pro", "$17"],
                ]
            },
            {
                "label": "Временно нет в наличии",
                "plans": [
                    ["Max ×5", "❌ нет"],
                    ["Max ×20", "❌ нет"],
                ]
            }
        ]
    },
    "⌨️ Cursor AI": {
        "sections": [
            {
                "label": "Новый акк + почта",
                "plans": [
                    ["Pro", "$17"],
                    ["Pro+ и Ultra", "❌ нет"],
                ]
            },
            {
                "label": "Продление",
                "plans": [
                    ["Pro", "$23.5"],
                    ["Pro+", "$66"],
                    ["Ultra", "$218.5"],
                ]
            }
        ]
    },
    "𝕏 Grok AI": {
        "sections": [
            {
                "label": "SuperGrok",
                "plans": [
                    ["Новый акк + почта", "$11"],
                    ["Продление", "$15"],
                ]
            },
            {
                "label": "Другое",
                "plans": [
                    ["CDK", "$17"],
                ]
            }
        ]
    },
    "🎶 Suno AI": {
        "sections": [
            {
                "label": "Индия (UPI)",
                "plans": [
                    ["Pro", "$12"],
                    ["Premier", "$33"],
                ]
            },
            {
                "label": "Другие страны",
                "plans": [
                    ["Pro", "$13"],
                    ["Premier", "$35"],
                ]
            }
        ]
    },
    "🎨 Krea AI": {
        "plans": [
            ["Basic", "$8"],
            ["Pro", "$30.8"],
            ["Max 40k", "$61.6"],
            ["Max 60k", "$92.4"],
            ["Max 80k", "$118.8"],
            ["Max 100k", "$145.2"],
        ]
    },
    "✨ Gamma AI": {
        "plans": [
            ["Plus", "$10.6"],
            ["Pro", "$22"],
        ]
    },
    "🖌️ Freepik AI": {
        "plans": [
            ["Essential", "$12"],
            ["Premium", "$21"],
            ["Premium Plus", "$44"],
        ]
    },
    "🎬 Runway ML": {
        "plans": [
            ["Standard", "$13.2"],
            ["Pro", "$30.8"],
            ["Unlimited", "$83.6"],
        ]
    },
    "🌟 Flair AI": {
        "plans": [
            ["Pro", "$8.8"],
            ["Pro+", "$30.8"],
        ]
    },
    "🎥 Pika Art AI": {
        "plans": [
            ["Standard", "$8.8"],
            ["Pro", "$30.8"],
            ["Fancy", "$83.6"],
        ]
    },
    "🦁 Leonardo AI": {
        "plans": [
            ["Essential", "$14.8"],
            ["Premium", "$34.8"],
            ["Ultimate", "$69"],
        ]
    },
    "🤖 Kling AI": {
        "sections": [
            {
                "label": "Новый аккаунт",
                "plans": [
                    ["Standard", "$8.8"],
                    ["Pro", "$31.5"],
                    ["Premier", "$72.2"],
                    ["Ultra", "$146.8"],
                ]
            },
            {
                "label": "Продление",
                "plans": [
                    ["Standard", "$10.9"],
                    ["Pro", "$39.4"],
                    ["Premier", "$97.2"],
                    ["Ultra", "$183.4"],
                ]
            }
        ]
    },
}

def load_catalog():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CATALOG

def save_catalog(catalog):
    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

def get_all_plans(catalog):
    """Возвращает список (сервис, секция_или_None, индекс_плана, название_плана, цена)"""
    result = []
    for svc_name, svc_data in catalog.items():
        if "plans" in svc_data:
            for i, (plan, price) in enumerate(svc_data["plans"]):
                result.append((svc_name, None, i, plan, price))
        elif "sections" in svc_data:
            for sec in svc_data["sections"]:
                for i, (plan, price) in enumerate(sec["plans"]):
                    result.append((svc_name, sec["label"], i, plan, price))
    return result

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
    catalog = load_catalog()
    services = list(catalog.keys())
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

# ── ADMIN PANEL ──────────────────────────────────────────────

def admin_services_keyboard(catalog):
    buttons = []
    row = []
    for name in catalog.keys():
        row.append(InlineKeyboardButton(name, callback_data=f"adm_svc:{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("❌ Выйти из админки", callback_data="adm_exit")])
    return InlineKeyboardMarkup(buttons)

def admin_plans_keyboard(svc_name, svc_data):
    buttons = []
    if "plans" in svc_data:
        for i, (plan, price) in enumerate(svc_data["plans"]):
            buttons.append([InlineKeyboardButton(
                f"{plan} — {price}", callback_data=f"adm_plan:{svc_name}||{i}||"
            )])
    elif "sections" in svc_data:
        for sec in svc_data["sections"]:
            for i, (plan, price) in enumerate(sec["plans"]):
                buttons.append([InlineKeyboardButton(
                    f"{plan} — {price}", callback_data=f"adm_plan:{svc_name}||{i}||{sec['label']}"
                )])
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="adm_back")])
    return InlineKeyboardMarkup(buttons)

# ── HANDLERS ─────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Здесь ты можешь посмотреть цены на подписки и оформить заказ.\n\nВыбери сервис:",
        reply_markup=main_menu_keyboard()
    )

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    catalog = load_catalog()
    await update.message.reply_text(
        "🔧 <b>Админ-панель</b>\nВыбери сервис для изменения цены:",
        parse_mode="HTML",
        reply_markup=admin_services_keyboard(catalog)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    catalog = load_catalog()

    # ── ADMIN CALLBACKS ──
    if data.startswith("adm_"):
        if update.effective_user.id not in ADMIN_IDS:
            return

        if data == "adm_back":
            await query.edit_message_text(
                "🔧 <b>Админ-панель</b>\nВыбери сервис:",
                parse_mode="HTML",
                reply_markup=admin_services_keyboard(catalog)
            )

        elif data == "adm_exit":
            await query.edit_message_text("✅ Вышел из админки.")

        elif data.startswith("adm_svc:"):
            svc_name = data[8:]
            svc_data = catalog.get(svc_name)
            if not svc_data:
                return
            await query.edit_message_text(
                f"🔧 <b>{svc_name}</b>\nВыбери тариф для изменения цены:",
                parse_mode="HTML",
                reply_markup=admin_plans_keyboard(svc_name, svc_data)
            )

        elif data.startswith("adm_plan:"):
            # format: adm_plan:svc_name||plan_index||section_label
            payload = data[9:]
            parts = payload.split("||")
            svc_name = parts[0]
            plan_idx = int(parts[1])
            sec_label = parts[2] if len(parts) > 2 else ""

            svc_data = catalog.get(svc_name)
            if "plans" in svc_data:
                plan_name, current_price = svc_data["plans"][plan_idx]
            else:
                sec = next(s for s in svc_data["sections"] if s["label"] == sec_label)
                plan_name, current_price = sec["plans"][plan_idx]

            context.user_data["editing"] = {
                "svc": svc_name,
                "idx": plan_idx,
                "sec": sec_label,
                "plan": plan_name,
            }
            await query.edit_message_text(
                f"✏️ <b>{svc_name}</b>\n"
                f"Тариф: <b>{plan_name}</b>\n"
                f"Текущая цена: <b>{current_price}</b>\n\n"
                f"Напиши новую цену (например: <code>$18</code> или <code>❌ нет</code>):",
                parse_mode="HTML"
            )
        return

    # ── USER CALLBACKS ──
    if data.startswith("svc:"):
        name = data[4:]
        svc_data = catalog.get(name)
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
        for name, svc_data in catalog.items():
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
    user_id = update.effective_user.id

    # ── ADMIN: сохранение новой цены ──
    if user_id in ADMIN_IDS and context.user_data.get("editing"):
        edit = context.user_data["editing"]
        new_price = update.message.text.strip()
        catalog = load_catalog()

        svc_data = catalog[edit["svc"]]
        if "plans" in svc_data:
            svc_data["plans"][edit["idx"]][1] = new_price
        else:
            sec = next(s for s in svc_data["sections"] if s["label"] == edit["sec"])
            sec["plans"][edit["idx"]][1] = new_price

        save_catalog(catalog)
        context.user_data["editing"] = None

        await update.message.reply_text(
            f"✅ Цена обновлена!\n\n"
            f"<b>{edit['svc']}</b>\n"
            f"{edit['plan']} — <b>{new_price}</b>",
            parse_mode="HTML",
            reply_markup=admin_services_keyboard(catalog)
        )
        return

    # ── USER: оформление заказа ──
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

        for aid in ADMIN_IDS:
            await context.bot.send_message(aid, order_text, parse_mode="HTML")
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
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
