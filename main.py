import asyncio
import db
import webserver
import logging

from config import discord_token
from bot.bot import Class_bot
from bot.context import BotContext
from utils.logger import log_error
from verification.asset_creator import VerifyView 

async def main() -> None:
    print("[SETUP] Setup starting...")

    print(f"[SETUP] Initialising database...")
    db.init_database()
    print(f"[SETUP] Initialised database!")
    
    print(f"[SETUP] Creating bot...")
    bot = Class_bot()

    print(f"[SETUP] Loading bot modules...")
    context = BotContext(
        db=db,
        log_error=log_error,
        verifyView=VerifyView
    )

    await bot.load_modules(context)
    print(f"[SETUP] Loaded bot modules!")

    print(f"[SETUP] Created bot!")

    # ---------- WEBSERVER SETUP ----------

    print(f"[SETUP] Starting up webserver...")
    asyncio.create_task(webserver.start_webserver())
    print(f"[SETUP] Started webserver!")

    # ---------- Bot startup ----------

    print(f"[SETUP] Starting bot...")

    try:
        await bot.start(discord_token)
    except Exception as e:
        print(f"[FATAL] Bot crashed on setup canceling... Error : {e}")
        return
    

# ------------------------------------------------------------ MAIN ------------------------------------------------------------

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    asyncio.run(main())