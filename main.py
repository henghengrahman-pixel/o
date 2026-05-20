import random
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from config import BOT_TOKEN, CHANNELS, BUTTONS, THREAD_ID
from game_list import GAMES

bot = Bot(token=BOT_TOKEN)
scheduler = AsyncIOScheduler()

# Fungsi untuk mendapatkan jam gacor (30 menit)
def get_gacor_period():
    now = datetime.now() + timedelta(hours=7)  # WIB
    start = now.replace(second=0, microsecond=0)
    end = start + timedelta(minutes=30)
    return start.strftime("%H:%M"), end.strftime("%H:%M")

# Generate pesan utama dengan 4 game acak
def generate_message():
    start, end = get_gacor_period()
    header = (
        "<b>🎰 RTP SLOT GACOR RUPIAHTOTO</b>\n"
        f"🕓 JAM GACOR : <b>{start} - {end} WIB</b>\n\n"
    )

    def bar(val):
        filled = max(0, min(10, round((val - 90) / 10 * 10)))
        return "█" * filled + "░" * (10 - filled)

    games = []
    for g in random.sample(GAMES, 4):
        rtp = random.randint(92, 98)
        games.append((g["name"].upper(), g["provider"].upper(), rtp))
    games.sort(key=lambda x: x[2], reverse=True)

    body = ""
    for name, prov, rtp in games:
        emoji = "🔥" if rtp >= 97 else ("⚡️" if rtp >= 95 else "✨")
        body += f"{emoji} <b>{name}</b> — <i>{prov}</i>\n🎯 {rtp}% {bar(rtp)}\n\n"

    footer = "🎯 Gacor Tiap Jam, Cuan Tiap Putaran!! Jaga Profit !!"
    return header + body + footer

# Kirim pesan ke semua channel
async def send_to_channels():
    now = datetime.utcnow() + timedelta(hours=7)  # WIB

    # Cek maintenance hari Kamis jam 07.00-08.59 WIB
    if now.weekday() == 3 and 7 <= now.hour < 9:
        maintenance_msg = (
            "⚙️ <b>WEBSITE RUPIAH TOTO SEDANG MAINTENANCE</b> ⚙️\n\n"
            "Untuk meningkatkan kenyamanan saat bermain, website sedang dalam pemeliharaan.\n"
            "Akan kembali normal pada pukul <b>09.00 WIB</b>.\n\nMohon bersabar, boskuu 🙏"
        )
        for channel in CHANNELS:
            try:
                await bot.send_message(
                    chat_id=channel,
                    text=maintenance_msg,
                    parse_mode=ParseMode.HTML,
                    message_thread_id=THREAD_ID
                )
            except Exception as e:
                print(f"❌ Error kirim maintenance ke {channel}: {e}")
        return

    # Kalau bukan jam maintenance, kirim RTP
    message = generate_message()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=BUTTONS['play'], url=BUTTONS['play_url'])],
        [InlineKeyboardButton(text=BUTTONS['chat'], url=BUTTONS['chat_url'])],
        [InlineKeyboardButton(text=BUTTONS['promo'], url=BUTTONS['promo_url'])]
    ])
    for channel in CHANNELS:
        try:
            await bot.send_message(
                chat_id=channel,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=buttons,
                message_thread_id=THREAD_ID
            )
        except Exception as e:
            print(f"❌ Error kirim ke {channel}: {e}")

# Start scheduler 30 menit
async def start_scheduler():
    scheduler.add_job(send_to_channels, 'interval', minutes=30)
    scheduler.start()
    await send_to_channels()
    while True:
        await asyncio.sleep(3600)

# Run bot
if __name__ == "__main__":
    asyncio.run(start_scheduler())
