import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from scoring import ScoringSystem

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ BOTFATHER
BOT_TOKEN = "8932498428:AAEgtUxkMQkai9LhyGlCjomZ6WLplb218Rk"
session = AiohttpSession(proxy="http://34.223.252.220:1001")
# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scoring = ScoringSystem()


# Состояния для FSM (машина состояний)
class ScoringStates(StatesGroup):
    waiting_for_bank = State()
    waiting_for_telegram = State()


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я AI-ассистент по альтернативному скорингу.\n\n"
        "Я проанализирую твою банковскую выписку и Telegram-канал, "
        "чтобы оценить благонадежность.\n\n"
        "📂 <b>Шаг 1:</b> Пришлите мне файл банковской выписки в формате <b>CSV</b>.",
        parse_mode="HTML"
    )
    await state.set_state(ScoringStates.waiting_for_bank)


# Обработка CSV файла
@dp.message(ScoringStates.waiting_for_bank, F.document)
async def process_bank_file(message: Message, state: FSMContext):
    if message.document.file_name.endswith('.csv'):
        file_path = "data/bank_upload.csv"
        await message.document.download(destination=file_path)
        await state.update_data(bank_file=file_path)

        await message.answer(
            "✅ Выписка принята!\n\n"
            " <b>Шаг 2:</b> Теперь пришлите экспорт Telegram-канала в формате <b>JSON</b>.",
            parse_mode="HTML"
        )
        await state.set_state(ScoringStates.waiting_for_telegram)
    else:
        await message.answer("❌ Это не CSV файл. Пожалуйста, пришлите файл с расширением .csv")


# Обработка JSON файла и запуск анализа
@dp.message(ScoringStates.waiting_for_telegram, F.document)
async def process_telegram_file(message: Message, state: FSMContext):
    if message.document.file_name.endswith('.json'):
        file_path = "data/telegram_upload.json"
        await message.document.download(destination=file_path)

        await message.answer("⏳ Анализирую цифровой след и финансовые потоки... Подождите пару секунд.")

        # Запускаем нашу систему скоринга
        data = await state.get_data()
        bank_analysis = scoring.analyze_bank_statement(data['bank_file'])
        telegram_analysis = scoring.analyze_telegram(file_path)
        final_result = scoring.calculate_final_score(bank_analysis, telegram_analysis)

        # Формируем красивое сообщение для Telegram
        profile = telegram_analysis['psychological_profile']

        # Текстовые "прогресс-бары" для Telegram
        def make_bar(score):
            filled = score
            empty = 10 - score
            return f"{'█' * filled}{'░' * empty} {score}/10"

        report = (
            f"🎯 <b>ИТОГОВАЯ ОЦЕНКА: {final_result['final_score']}/100</b>\n"
            f"{final_result['recommendation']}\n\n"
            f"🏦 <b>Банковский скоринг:</b> {final_result['base_score']}\n"
            f"📈 <b>AI-корректировка (Telegram):</b> {'+' if final_result['telegram_adjustment'] >= 0 else ''}{final_result['telegram_adjustment']}\n\n"
            f"🧠 <b>Психологический портрет:</b>\n"
            f"• Стабильность работы: {make_bar(profile['work_stability'])}\n"
            f"• Фин. грамотность: {make_bar(profile['financial_literacy'])}\n"
            f"• Ответственность: {make_bar(profile['responsibility'])}\n\n"
            f"✅ <b>Позитивные сигналы:</b>\n"
            f"{''.join([f'  • {s}\n' for s in telegram_analysis['positive_signals']])}\n"
            f"⚠️ <b>Факторы риска:</b>\n"
            f"{''.join([f'  • {s}\n' for s in telegram_analysis['negative_signals']])}"
        )

        await message.answer(report, parse_mode="HTML")
        await message.answer("🔄 Хотите проанализировать другого заемщика? Нажмите /start", parse_mode="HTML")
        await state.clear()
    else:
        await message.answer("❌ Это не JSON файл. Пожалуйста, пришлите файл с расширением .json")


# Обработка команды /start в середине процесса (сброс)
@dp.message(Command("start"))
async def reset_state(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())