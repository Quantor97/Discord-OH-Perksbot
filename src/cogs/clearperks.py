import discord
import settings
from discord.ext import commands
from database import Database

logger = settings.logging.getLogger("bot")

class ClearPerks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command(name="clearperks", help="Clear your perks")
    async def clearperks(self, ctx: commands.Context):
        try:
            if self.db.user_has_perks(ctx.author.id):
                self.db.clear_user_perks(ctx.author.id)
                await ctx.send("Your perks have been cleared!" ,delete_after=5)
            else:
                await ctx.send("You have no perks to clear.", delete_after=5)
        except Exception as e:
            await ctx.send("An error occurred while clearing your perks.", delete_after=5)
            logger.error(f"Error clearing perks: {e}")
        
def setup(bot):
    bot.add_cog(ClearPerks(bot))