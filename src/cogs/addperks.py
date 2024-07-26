import discord
import settings
from discord.ext import commands
from database import Database
from config import MAX_PERKS

logger = settings.logging.getLogger("bot")

class PerkSelectionView(discord.ui.View):
    def __init__(self, perks, db, user_id, user_name):
        super().__init__(timeout=300)
        self.db = db
        self.user_id = user_id
        self.user_name = user_name
        self.chunk_size = 25
        self.selected_perks = []
        self.dropdown_perks = {}

        # Fetch the existing perks of the user
        self.existing_perks = self.db.get_user_perks(user_id)
        self.selected_perks.extend(self.existing_perks)

        # Split perks into chunks of 25
        chunked_perks = [perks[i:i + self.chunk_size] for i in range(0, len(perks), self.chunk_size)]

        for chunk in chunked_perks:
            options = [
                discord.SelectOption(label=perk, value=perk, default=(perk in self.existing_perks)) 
                for perk in chunk
            ]
            
            select = discord.ui.Select(
                placeholder="Choose your perks",
                options=options,
                max_values=len(options),
                min_values=0
            )

            self.dropdown_perks[select] = chunk
            select.callback = self.make_select_callback(select)
            self.add_item(select)

        submit_button = discord.ui.Button(label="Submit", style=discord.ButtonStyle.primary)
        submit_button.callback = self.submit
        self.add_item(submit_button)

        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        cancel_button.callback = self.cancel
        self.add_item(cancel_button)

    async def on_timeout(self) -> None:
        # This method is called when the view times out
        for item in self.children:
            item.disabled = True

        await self.message.delete(delay=10)  # Deletes the message after an additional 10 seconds

    async def cancel(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This interaction is not for you.", ephemeral=True, delete_after=5)
            return

        await interaction.response.send_message("Perk selection cancelled.", ephemeral=True, delete_after=5)
        await interaction.message.delete()

    def make_select_callback(self, select):
        async def select_callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This interaction is not for you.", ephemeral=True, delete_after=5)
                return

            selected_values = interaction.data['values']

            # Remove any previously selected perks from this dropdown
            for perk in self.dropdown_perks[select]:
                if perk in self.selected_perks:
                    self.selected_perks.remove(perk)

            # Add the newly selected perks from this dropdown
            self.selected_perks.extend(selected_values)
            self.selected_perks = list(set(self.selected_perks))  # Ensure unique perks

            await interaction.response.send_message("Perks selected, click Submit when done.", ephemeral=True, delete_after=2)
        
        return select_callback

    async def submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This interaction is not for you.", ephemeral=True, delete_after=5)
            return

        # Merge selected perks with existing perks
        selected_perks = list(set(self.selected_perks))  # Ensure unique perks

        if len(selected_perks) > MAX_PERKS:
            await interaction.response.send_message(f"[Error] You can select up to {MAX_PERKS} perks.", ephemeral=True, delete_after=5)
            return
        elif not selected_perks:
            await interaction.response.send_message("[Error] You must select at least one perk.", ephemeral=True, delete_after=5)
            return

        try:
            
            if self.db.user_has_perks(self.user_id):
                self.db.update_user_perks(self.user_id, self.user_name, selected_perks)
                await interaction.response.send_message("Your perks have been updated!", ephemeral=True, delete_after=5)
            else:
                self.db.add_user_perks(self.user_id, self.user_name, selected_perks)
                await interaction.response.send_message("Your perks have been saved!", ephemeral=True, delete_after=5)
            
            # Delete the message containing the view
            await interaction.message.delete()
        except Exception as e:
            logger.error(f"Error processing perk selection: {e}")
            await interaction.response.send_message("An error occurred while saving your perks.", ephemeral=True, delete_after=10)

class AddPerks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command(name="addperks", help="Select your perks")
    async def addperks(self, ctx):
        try:
            # Fetch perks from the database
            perks = self.db.get_perks()
            if not perks:
                await ctx.send("[Info] No perks available at the moment", delete_after=5)
                return
            
            # Show dropdowns and submit button
            view = PerkSelectionView(perks, self.db, ctx.author.id, ctx.author.display_name)
            await ctx.send(f"{ctx.author.display_name} - Select your perks and then click Submit:", view=view)
        except Exception as e:
            logger.error(f"Error in addperks command: {e}")
            await ctx.send("An error occurred while fetching perks.", delete_after=10)

def setup(bot):
    bot.add_cog(AddPerks(bot))