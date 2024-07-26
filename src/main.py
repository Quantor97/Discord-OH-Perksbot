import discord
from config import DISCORD_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import update_perks
from botmanager import BotManager

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = BotManager(command_prefix='!', intents=intents)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_perks, 'interval', days=1)
    scheduler.start()

    bot.load_extension('cogs.viewperks')
    bot.load_extension('cogs.addperks')
    bot.load_extension('cogs.clearperks')
    bot.load_extension('cogs.updatedb')
    bot.add_check(bot.channel_check)

    bot.run(DISCORD_TOKEN)