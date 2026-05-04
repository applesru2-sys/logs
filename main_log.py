import discord
from discord.ext import commands

# Канал, откуда бот ЧИТАЕТ системные данные (от селф-бота)
LISTEN_CHANNEL_ID = 1500991511385342143

# Канал, куда бот ПИШЕТ красивые отчеты для людей
REPORT_CHANNEL_ID = 1500991763718996249


class VoiceTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Игнорируем свои же сообщения
        if message.author == self.bot.user:
            return

        # Слушаем только технический канал от селф-бота
        if message.channel.id != LISTEN_CHANNEL_ID:
            return

        # Находим канал, куда будем отправлять красивые отчеты
        report_channel = self.bot.get_channel(REPORT_CHANNEL_ID)
        if not report_channel:
            print(f"❌ Ошибка: Основной бот не видит канал для отчетов ({REPORT_CHANNEL_ID})")
            return

        # --- ОБРАБОТКА ЗАХОДА ---
        if message.content.startswith("!voice_join|"):
            data = message.content.split('|')
            if len(data) == 4:
                user_id = data[1]
                channel_id = data[2]
                time_start = data[3]

                # Формируем красивое сообщение и отправляем
                text = f"🟢 <@{user_id}> **зашел** в канал <#{channel_id}> в `{time_start}`"
                await report_channel.send(text)

        # --- ОБРАБОТКА ВЫХОДА ---
        elif message.content.startswith("!voice_leave|"):
            data = message.content.split('|')
            if len(data) == 5:
                user_id = data[1]
                channel_id = data[2]
                time_end = data[3]
                seconds_spent = int(data[4])

                # Переводим скучные секунды в удобные минуты и секунды
                minutes = seconds_spent // 60
                seconds = seconds_spent % 60

                text = f"🔴 <@{user_id}> **вышел** из канала <#{channel_id}> в `{time_end}`.\n⏳ Просидел: **{minutes} мин. {seconds} сек.**"
                await report_channel.send(text)

                # Здесь же ты можешь добавить код для записи этих секунд в sqlite3!


# Загрузка модуля
async def setup(bot):
    await bot.add_cog(VoiceTracker(bot))
    print("✅ Модуль VoiceTracker успешно подключен! Читаю логи и пишу отчеты.")