import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "8882945235:AAGlkOeFY17bxsb_rVxSaTpvDlanQZm2O3w")
ADMIN_IDS = [781922474, 8320287292]

logging.basicConfig(level=logging.INFO)

PRICES_FILE = "prices.json"

DEFAULT_CATALOG = {
    "🎵 Spotify": {
        "sections": [
            {"label": "Standard", "plans": [["1 месяц", "$2.2"], ["12 месяцев", "$19"]]},
            {"label": "Platinum", "plans": [["1 месяц", "$5"], ["4.5 месяца", "$20"]]},
            {"label": "Другие тарифы", "plans": [["Individual", "$2.3"], ["Duo", "$3.2"], ["Family", "$3.5"]]}
        ]
    },
    "🎮 Xbox Game Pass": {
        "sections": [
            {"label": "Ultimate — любой акк (без подписки)", "plans": [["1 месяц", "$14.8"], ["2 месяца", "$29.6"], ["3 месяца", "$34.3"], ["5 месяцев", "$55.6"], ["7 месяцев", "$67.4"], ["9 месяцев", "$91.1"], ["12+1 мес", "$116"], ["Premium 1м (не Ultimate)", "$9.5"]]},
            {"label": "Ultimate — новый акк (не было подписок)", "plans": [["3 месяца", "$29.6"], ["5 месяцев", "$45"], ["7 месяцев", "$62.7"], ["9 месяцев", "$80.5"], ["12+1 мес", "$105.3"]]},
            {"label": "PC — только ПК", "plans": [["12 месяцев", "$68.6"]]}
        ]
    },
    "🖼️ Midjourney": {"plans": [["Basic", "$9"], ["Standard", "$22"], ["Pro", "$44"]]},
    "🤖 ChatGPT Plus": {
        "sections": [
            {"label": "Доступно", "plans": [["По данным/токену", "$16.5"], ["По данным/токену (срочно)", "$18"], ["По ссылке", "$24"]]},
            {"label": "Временно нет в наличии", "plans": [["Новый акк + почта", "❌ нет"]]}
        ]
    },
    "✦ Claude AI": {
        "sections": [
            {"label": "Доступно", "plans": [["Pro", "$17"]]},
            {"label": "Временно нет в наличии", "plans": [["Max ×5", "❌ нет"], ["Max ×20", "❌ нет"]]}
        ]
    },
    "⌨️ Cursor AI": {
        "sections": [
            {"label": "Новый акк + почта", "plans": [["Pro", "$17"], ["Pro+ и Ultra", "❌ нет"]]},
            {"label": "Продление", "plans": [["Pro", "$23.5"], ["Pro+", "$66"], ["Ultra", "$218.5"]]}
        ]
    },
    "𝕏 Grok AI": {
        "sections": [
            {"label": "SuperGrok", "plans": [["Новый акк + почта", "$11"], ["Продление", "$15"]]},
            {"label": "Другое", "plans": [["CDK", "$17"]]}
        ]
    },
    "🎶 Suno AI": {
        "sections": [
            {"label": "Индия (UPI)", "plans": [["Pro", "$12"], ["Premier", "$33"]]},
            {"label": "Другие страны", "plans": [["Pro", "$13"], ["Premier", "$35"]]}
        ]
    },
    "🎨 Krea AI": {"plans": [["Basic", "$8"], ["Pro", "$30.8"], ["Max 40k", "$61.6"], ["Max 60k", "$92.4"], ["Max 80k", "$118.8"], ["Max 100k", "$145.2"]]},
    "✨ Gamma AI": {"plans": [["Plus", "$10.6"], ["Pro", "$22"]]},
    "🖌️ Freepik AI": {"plans": [["Essential", "$12"], ["Premium", "$21"], ["Premium Plus", "$44"]]},
    "🎬 Runway ML": {"plans": [["Standard", "$13.2"], ["Pro", "$30.8"], ["Unlimited", "$83.6"]]},
    "🌟 Flair AI": {"plans": [["Pro", "$8.8"], ["Pro+", "$30.8"]]},
    "🎥 Pika Art AI": {"plans": [["Standard", "$8.8"], ["Pro", "$30.8"], ["Fancy", "$83.6"]]},
    "🦁 Leonardo AI": {"plans": [["Essential", "$14.8"], ["Premium", "$34.8"], ["Ultimate", "$69"]]},
    "🤖 Kling AI": {
        "sections": [
            {"label": "Новый аккаунт", "plans": [["Standard", "$8.8"], ["Pro", "$31.5"], ["Premier", "$72.2"], ["Ultra", "$146.8"]]},
            {"label": "Продление", "plans": [["Standard", "$10.9"], ["Pro", "$39.4"], ["Premier", "$97.2"], ["Ultra", "$183.4"]]}
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

# ── REPLY KEYBOARDS (нижняя панель) ──

def user_reply_keyboard():
    return ReplyKeyboardMarkup(
        [["📋 Прайс", "💬 Написать для заказа"]],
        resize_keyboard=True
    )

def admin_reply_keyboard():
    return ReplyKeyboardMarkup(
        [["📋 Прайс", "💬 Написать для заказа"],
         ["🔧 Админ-панель"]],
        resize_keyboard=True
    )

# ── INLINE KEYBOARDS ──

def main_menu_inline():
    catalog = load_catalog()
    buttons = []
    row = []
    for i, name in enumerate(catalog.keys()):
        row.append(InlineKeyboardButton(name, callback_data=f"svc:{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("📋 Весь прайс", callback_data="all")])
    return InlineKeyboardMarkup(buttons)

def admin_main_inline():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Изменить цену", callback_data="adm_edit")],
        [InlineKeyboardButton("➕ Добавить сервис", callback_data="adm_add_svc")],
        [InlineKeyboardButton("➕ Добавить тариф", callback_data="adm_add_plan")],
        [InlineKeyboardButton("🗑 Удалить сервис", callback_data="adm_del_svc")],
        [InlineKeyboardButton("❌ Закрыть", callback_data="adm_exit")],
    ])

def admin_services_inline(catalog, back="adm_main"):
    buttons = []
    row = []
    for name in catalog.keys():
        row.append(InlineKeyboardButton(name, callback_data=f"adm_svc:{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data=back)])
    return InlineKeyboardMarkup(buttons)

def admin_plans_inline(svc_name, svc_data):
    buttons = []
    if "plans" in svc_data:
        for i, (plan, price) in enumerate(svc_data["plans"]):
            buttons.append([InlineKeyboardButton(f"{plan} — {price}", callback_data=f"adm_plan:{svc_name}||{i}||")])
    elif "sections" in svc_data:
        for sec in svc_data["sections"]:
            for i, (plan, price) in enumerate(sec["plans"]):
                buttons.append([InlineKeyboardButton(f"{plan} — {price}", callback_data=f"adm_plan:{svc_name}||{i}||{sec['label']}")])
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="adm_edit")])
    return InlineKeyboardMarkup(buttons)

def admin_del_services_inline(catalog):
    buttons = []
    row = []
    for name in catalog.keys():
        row.append(InlineKeyboardButton(name, callback_data=f"adm_del_confirm:{name}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="adm_main")])
    return InlineKeyboardMarkup(buttons)

# ── HANDLERS ──

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id in ADMIN_IDS
    reply_kb = admin_reply_keyboard() if is_admin else user_reply_keyboard()
    await update.message.reply_text(
        "👋 Привет! Здесь можно посмотреть цены на подписки.\n\nВыбери сервис:",
        reply_markup=reply_kb
    )
    await update.message.reply_text("Каталог:", reply_markup=main_menu_inline())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "📋 Прайс":
        await update.message.reply_text("Выбери сервис:", reply_markup=main_menu_inline())

    elif text == "💬 Написать для заказа":
        await update.message.reply_text("Для оформления заказа напиши сюда: @fursovhub")

    elif text == "🔧 Админ-панель" and user_id in ADMIN_IDS:
        await update.message.reply_text(
            "🔧 <b>Админ-панель</b>\nЧто хочешь сделать?",
            parse_mode="HTML",
            reply_markup=admin_main_inline()
        )

    # Обработка состояний
    elif context.user_data.get("state") == "editing_price":
        edit = context.user_data["editing"]
        new_price = text.strip()
        catalog = load_catalog()
        svc_data = catalog[edit["svc"]]
        if "plans" in svc_data:
            svc_data["plans"][edit["idx"]][1] = new_price
        else:
            sec = next(s for s in svc_data["sections"] if s["label"] == edit["sec"])
            sec["plans"][edit["idx"]][1] = new_price
        save_catalog(catalog)
        context.user_data["state"] = None
        context.user_data["editing"] = None
        await update.message.reply_text(
            f"✅ Цена обновлена!\n<b>{edit['svc']}</b>\n{edit['plan']} — <b>{new_price}</b>",
            parse_mode="HTML",
            reply_markup=admin_main_inline()
        )

    elif context.user_data.get("state") == "adding_svc_name":
        context.user_data["new_svc_name"] = text.strip()
        context.user_data["state"] = "adding_svc_plan_name"
        await update.message.reply_text("Введи название первого тарифа (например: Pro):")

    elif context.user_data.get("state") == "adding_svc_plan_name":
        context.user_data["new_plan_name"] = text.strip()
        context.user_data["state"] = "adding_svc_plan_price"
        await update.message.reply_text("Введи цену (например: $15):")

    elif context.user_data.get("state") == "adding_svc_plan_price":
        svc_name = context.user_data["new_svc_name"]
        plan_name = context.user_data["new_plan_name"]
        price = text.strip()
        catalog = load_catalog()
        catalog[svc_name] = {"plans": [[plan_name, price]]}
        save_catalog(catalog)
        context.user_data["state"] = None
        await update.message.reply_text(
            f"✅ Сервис добавлен!\n<b>{svc_name}</b>\n{plan_name} — {price}",
            parse_mode="HTML",
            reply_markup=admin_main_inline()
        )

    elif context.user_data.get("state") == "adding_plan_name":
        context.user_data["new_plan_name"] = text.strip()
        context.user_data["state"] = "adding_plan_price"
        await update.message.reply_text("Введи цену (например: $15):")

    elif context.user_data.get("state") == "adding_plan_price":
        edit = context.user_data["editing"]
        plan_name = context.user_data["new_plan_name"]
        price = text.strip()
        catalog = load_catalog()
        svc_data = catalog[edit["svc"]]
        if "plans" in svc_data:
            svc_data["plans"].append([plan_name, price])
        elif "sections" in svc_data:
            svc_data["sections"][0]["plans"].append([plan_name, price])
        save_catalog(catalog)
        context.user_data["state"] = None
        await update.message.reply_text(
            f"✅ Тариф добавлен в <b>{edit['svc']}</b>\n{plan_name} — {price}",
            parse_mode="HTML",
            reply_markup=admin_main_inline()
        )

    else:
        await update.message.reply_text("Выбери сервис:", reply_markup=main_menu_inline())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    catalog = load_catalog()
    user_id = update.effective_user.id

    # ── ADMIN ──
    if data.startswith("adm_"):
        if user_id not in ADMIN_IDS:
            return

        if data == "adm_main":
            await query.edit_message_text(
                "🔧 <b>Админ-панель</b>\nЧто хочешь сделать?",
                parse_mode="HTML",
                reply_markup=admin_main_inline()
            )

        elif data == "adm_exit":
            await query.edit_message_text("✅ Закрыто.")

        elif data == "adm_edit":
            await query.edit_message_text(
                "✏️ Выбери сервис для изменения цены:",
                parse_mode="HTML",
                reply_markup=admin_services_inline(catalog, back="adm_main")
            )

        elif data == "adm_add_svc":
            context.user_data["state"] = "adding_svc_name"
            await query.edit_message_text("➕ Введи название нового сервиса (например: 🎯 Новый AI):")

        elif data == "adm_add_plan":
            await query.edit_message_text(
                "➕ Выбери сервис, в который добавить тариф:",
                reply_markup=admin_services_inline(catalog, back="adm_main")
            )
            context.user_data["state"] = "selecting_svc_for_plan"

        elif data == "adm_del_svc":
            await query.edit_message_text(
                "🗑 Выбери сервис для удаления:",
                reply_markup=admin_del_services_inline(catalog)
            )

        elif data.startswith("adm_del_confirm:"):
            svc_name = data[16:]
            await query.edit_message_text(
                f"⚠️ Удалить <b>{svc_name}</b>?",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Да, удалить", callback_data=f"adm_del_do:{svc_name}")],
                    [InlineKeyboardButton("◀️ Отмена", callback_data="adm_del_svc")]
                ])
            )

        elif data.startswith("adm_del_do:"):
            svc_name = data[11:]
            if svc_name in catalog:
                del catalog[svc_name]
                save_catalog(catalog)
            await query.edit_message_text(
                f"✅ Сервис <b>{svc_name}</b> удалён.",
                parse_mode="HTML",
                reply_markup=admin_main_inline()
            )

        elif data.startswith("adm_svc:"):
            svc_name = data[8:]
            svc_data = catalog.get(svc_name)
            if not svc_data:
                return
            state = context.user_data.get("state")
            if state == "selecting_svc_for_plan":
                context.user_data["editing"] = {"svc": svc_name}
                context.user_data["state"] = "adding_plan_name"
                await query.edit_message_text(f"➕ Введи название нового тарифа для <b>{svc_name}</b>:", parse_mode="HTML")
            else:
                await query.edit_message_text(
                    f"✏️ <b>{svc_name}</b>\nВыбери тариф:",
                    parse_mode="HTML",
                    reply_markup=admin_plans_inline(svc_name, svc_data)
                )

        elif data.startswith("adm_plan:"):
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
            context.user_data["editing"] = {"svc": svc_name, "idx": plan_idx, "sec": sec_label, "plan": plan_name}
            context.user_data["state"] = "editing_price"
            await query.edit_message_text(
                f"✏️ <b>{svc_name}</b>\nТариф: <b>{plan_name}</b>\nТекущая цена: <b>{current_price}</b>\n\nНапиши новую цену:",
                parse_mode="HTML"
            )
        return

    # ── USER ──
    if data.startswith("svc:"):
        name = data[4:]
        svc_data = catalog.get(name)
        if not svc_data:
            return
        text = format_service(name, svc_data)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Заказать у @fursovhub", url="https://t.me/fursovhub")],
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

    elif data == "back":
        await query.edit_message_text("Выбери сервис:", reply_markup=main_menu_inline())

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
