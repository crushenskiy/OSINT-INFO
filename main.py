import aiogram
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
import asyncio
import json
import os
from engine import OSINTEngine

# Если токен передан через Render Environment Variables, он подхватится оттуда
# Иначе вставь токен прямо в кавычки
TOKEN = os.getenv("BOT_TOKEN", "9088331923:AAGkRbdmIpMLPjsuEFgVk--rQD5iba35mTE")

router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()
engine = OSINTEngine()

@router.message(F.text.startswith("/start"))
async def cmd_start(message: Message):
    await message.answer(
        "🕵️ Eye of God OSINT Bot\n\n"
        "Команды:\n"
        "/passport [номер] - Анализ паспорта\n"
        "/car [госномер] - Анализ авто\n"
        "/socials [юзернейм] - Поиск в соцсетях\n"
        "/ip [ip-адрес] - Анализ IP\n"
        "/name [имя] - Анализ по имени\n"
        "/email [почта] - Анализ почты\n"
        "Или просто отправь фото для EXIF-анализа."
    )

@router.message(F.text.startswith("/passport"))
async def handle_passport(message: Message):
    try:
        p = message.text.split()[1]
        res = await engine.execute("passport", p)
        await message.answer(f"📄 Паспорт: {p}\n{json.dumps(res, indent=2, ensure_ascii=False)}")
    except IndexError:
        await message.answer("Использование: /passport [номер]")

@router.message(F.text.startswith("/car"))
async def handle_car(message: Message):
    try:
        p = message.text.split()[1]
        res = await engine.execute("car", p)
        await message.answer(f"🚗 Авто: {p}\n{json.dumps(res, indent=2, ensure_ascii=False)}")
    except IndexError:
        await message.answer("Использование: /car [госномер]")

@router.message(F.text.startswith("/socials"))
async def handle_socials(message: Message):
    try:
        u = message.text.split()[1]
        res = await engine.execute("socials", u)
        await message.answer(f"🌐 Соцсети: {u}\n{json.dumps(res, indent=2, ensure_ascii=False)}")
    except IndexError:
        await message.answer("Использование: /socials [юзернейм]")

@router.message(F.photo)
async def handle_photo(message: Message):
    try:
        f = await bot.download(message.photo[-1].file_id)
        res = await engine.execute("photo", None, f)
        await message.answer(f"📸 Анализ фото:\n{json.dumps(res, indent=2, ensure_ascii=False)}")
    except Exception as e:
        await message.answer(f"Ошибка при обработке фото: {e}")

@router.message(F.text.startswith("/ip"))
async def handle_ip(message: Message):
    try:
        ip = message.text.split()[1]
        res = await engine.execute("ip", ip)
        await message.answer(f"🌍 IP: {ip}\n{json.dumps(res, indent=2, ensure_ascii=False)}")
    except IndexError:
        await message.answer("Использование: /ip [ip-адрес]")

@router.message(F.text.startswith("/name"))
async def handle_name(message: Message):
    n = " ".join(message.text.split()[1:])
    if not n:
        await message.answer("Использование: /name [имя фамилия]")
        return
    res = await engine.execute("name", n)
    await message.answer(f"👤 Имя: {n}\n{json.dumps(res, indent=2, ensure_ascii=False)}")

@router.message(F.text.startswith("/email"))
async def handle_email(message: Message):
    try:
        e = message.text.split()[1]
        res = await engine.execute("email", e)
        await message.answer(f"📧 Email: {e}\n{json.dumps(res, indent=2, ensure_ascii=False)}")
    except IndexError:
        await message.answer("Использование: /email [адрес]")

async def main():
    dp.include_router(router)
    print("Bot is starting...")
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
