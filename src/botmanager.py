from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import settings

logger = settings.logging.getLogger("bot")

ALLOWED_CHANNELS = [
    1266190130432180285,
    1265348779393941586
]

class BotManager(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user.name} ({self.user.id})")

    async def channel_check(self, ctx):
        return ctx.channel.id in ALLOWED_CHANNELS

    async def on_command_error(self, context: commands.Context, exception: commands.CommandError) -> None:
        if isinstance(exception, commands.CheckFailure):
            return
