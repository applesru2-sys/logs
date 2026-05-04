import discord
import os
from datetime import datetime
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# === НАСТРОЙКИ ===
TOKEN = os.environ.get("TOKEN")

TARGET_CHANNELS = [
    1186721255135654058, 1472260979692797954, 1458991222709424423,
    1043603628809793626, 1192856954977144953, 1030820272539959306,
    1209562056743714827, 989919653537144892, 1495819013324804206,
    1198359296379986010, 1424789420564811827, 1377225613181583460,
    1413039743272484935, 1377225544432619611, 1464613639557349448,
    1236303534178439269, 1348267680074829907
]

TARGET_ROLE_ID = 989980848260546620
OUTPUT_CHANNEL_ID = 1500991511385342143


class VoiceTracker(discord.Client):
    def __init__(self):
        super().__init__()
        self.active_sessions = {}

    async def on_ready(self):
        print(f"🚀 Бот-шпион {self.user.name} запущен! Слушаю каналы...")

    async def on_voice_state_update(self, member, before, after):
        has_role = any(role.id == TARGET_ROLE_ID for role in member.roles)
        if not has_role:
            return

        user_id = str(member.id)
        now = datetime.now()

        joined_target = after.channel and after.channel.id in TARGET_CHANNELS
        left_target = before.channel and before.channel.id in TARGET_CHANNELS

        # 1. Пользователь ЗАШЕЛ
        if joined_target and not left_target:
            self.active_sessions[user_id] = {
                "start_time": now,
                "channel_id": after.channel.id
            }
            await self.send_join_log(user_id, after.channel.id, now)
            print(f"📥 {member.name} ЗАШЕЛ")

        # 2. Пользователь ВЫШЕЛ
        elif left_target and not joined_target:
            if user_id in self.active_sessions:
                session = self.active_sessions.pop(user_id)
                await self.send_leave_log(user_id, session["channel_id"], session["start_time"], now)
                print(f"📤 {member.name} ВЫШЕЛ")

        # 3. Пользователь ПЕРЕПРЫГНУЛ между отслеживаемыми каналами
        elif left_target and joined_target and before.channel.id != after.channel.id:
            # Оформляем выход из старого канала
            if user_id in self.active_sessions:
                session = self.active_sessions.pop(user_id)
                await self.send_leave_log(user_id, session["channel_id"], session["start_time"], now)

            # Оформляем заход в новый канал
            self.active_sessions[user_id] = {
                "start_time": now,
                "channel_id": after.channel.id
            }
            await self.send_join_log(user_id, after.channel.id, now)
            print(f"🔄 {member.name} ПЕРЕШЕЛ")

    async def send_join_log(self, user_id, channel_id, start_dt):
        """Отправляет сигнал о ЗАХОДЕ"""
        output_channel = self.get_channel(OUTPUT_CHANNEL_ID)
        if output_channel:
            start_str = start_dt.strftime("%d.%m.%Y %H:%M:%S")
            msg = f"!voice_join|{user_id}|{channel_id}|{start_str}"
            try:
                await output_channel.send(msg)
            except Exception:
                pass

    async def send_leave_log(self, user_id, channel_id, start_dt, end_dt):
        """Отправляет сигнал о ВЫХОДЕ (с подсчетом секунд)"""
        output_channel = self.get_channel(OUTPUT_CHANNEL_ID)
        if output_channel:
            duration_seconds = int((end_dt - start_dt).total_seconds())
            end_str = end_dt.strftime("%d.%m.%Y %H:%M:%S")
            msg = f"!voice_leave|{user_id}|{channel_id}|{end_str}|{duration_seconds}"
            try:
                await output_channel.send(msg)
            except Exception:
                pass


client = VoiceTracker()
client.run(TOKEN)