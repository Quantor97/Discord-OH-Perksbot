import scraper
from discord.ext import commands

class UpdateDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='updatedb', aliases=['update_db'])
    @commands.has_guild_permissions(administrator=True, manage_guild=True)
    async def update_db(self, ctx):
        # Update the database
        await ctx.send("Updating the database...")
        perks_updated = scraper.update_perks()

        if perks_updated:
            await ctx.send("Database updated!")
        else :
            await ctx.send("An error occurred while updating the database.")
            
def setup(bot):
    bot.add_cog(UpdateDB(bot))