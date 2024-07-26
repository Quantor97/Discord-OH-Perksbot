import discord
import settings
from discord.ext import commands
from database import Database

logger = settings.logging.getLogger("bot")

class PerkInfoButton(discord.ui.Button):
    def __init__(self, perk_id, perk_name, db):
        super().__init__(label=perk_name, style=discord.ButtonStyle.primary)
        self.perk_id = perk_id
        self.db = db

    async def callback(self, interaction: discord.Interaction):
        perk_info = self.db.get_perk_info(self.perk_id)
        if perk_info:
            embed = discord.Embed(title=perk_info['name'], color=discord.Color.blue())
            embed.add_field(name="Type", value=perk_info['type'], inline=False)
            embed.add_field(name="Specialization", value=perk_info['specialization'], inline=False)
            embed.add_field(name="Specialization Effects", value=perk_info['specialization_effects'], inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Perk information not found.", ephemeral=True, delete_after=5)

class PerkNameInputModal(discord.ui.Modal):
    def __init__(self, db, user_id):
        super().__init__(title="Search by Perk Name")
        self.db = db
        self.user_id = user_id

        self.perk_name_input = discord.ui.InputText(label="Enter perk name", placeholder="perk name", required=True)
        self.add_item(self.perk_name_input)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This interaction is not for you.", ephemeral=True, delete_after=10)
            return

        try:
            perk_name = self.perk_name_input.value
            perks = self.db.get_users_with_perk(perk_name)
            if perks:
                embed = discord.Embed(title=f"Users with perks '{self.perk_name_input.value}'", color=discord.Color.green())
                for perk in perks:
                    perks_list = '\n'.join([f"- {user}" for user in perk["users"]])
                    embed.add_field(name=perk["name"], value=perks_list, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                    
            else:
                await interaction.response.send_message(f"No users found with perk matching '{perk_name}'.", ephemeral=True, delete_after=5)
        except Exception as e:
            logger.error(f"Error processing perk search by name: {e}")
            await interaction.response.send_message("An error occurred while searching for perks.", ephemeral=True, delete_after=10)

class PerkSearchView(discord.ui.View):
    def __init__(self, db, user_id):
        super().__init__(timeout=30)
        self.db = db
        self.user_id = user_id

        # Add a dropdown for perk types
        perk_types = self.db.get_perk_types()
        type_options = [discord.SelectOption(label=perk_type, value=perk_type) for perk_type in perk_types]
        self.perk_type_select = discord.ui.Select(placeholder="Choose a perk type", options=type_options, max_values=1)
        self.perk_type_select.callback = self.select_type_callback
        self.add_item(self.perk_type_select)

        # Add a dropdown for perk specializations
        perk_specializations = self.db.get_perk_specializations()
        specialization_options = [discord.SelectOption(label=specialization, value=specialization) for specialization in perk_specializations]
        self.perk_specialization_select = discord.ui.Select(placeholder="Choose a perk specialization", options=specialization_options, max_values=1)
        self.perk_specialization_select.callback = self.select_specialization_callback
        self.add_item(self.perk_specialization_select)

        # Add a button to open the perk name input modal
        name_input_button = discord.ui.Button(label="Search by Perk Name", style=discord.ButtonStyle.primary)
        name_input_button.callback = self.open_name_input
        self.add_item(name_input_button)

        # Add a button to view all users with their perks
        view_all_button = discord.ui.Button(label="View All", style=discord.ButtonStyle.secondary)
        view_all_button.callback = self.view_all_callback
        self.add_item(view_all_button)
    
    async def on_timeout(self) -> None:
        # This method is called when the view times out
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)
        await self.message.delete(delay=10)  # Deletes the message after an additional 10 seconds

    async def select_type_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            return

        try:
            perk_type = self.perk_type_select.values[0]
            users_with_perks = self.db.get_users_with_perk_type(perk_type)
            if users_with_perks:
                embed = discord.Embed(title=f"Users with perks of type '{perk_type}'", color=discord.Color.green())
                for user, perks in users_with_perks.items():
                    perks_list = '\n'.join([f"- {perk}" for perk in perks])
                    embed.add_field(name=user, value=perks_list, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(f"No users found with perks of type '{perk_type}'.", ephemeral=True, delete_after=5)
        except Exception as e:
            logger.error(f"Error processing perk search by type: {e}")
            await interaction.response.send_message("An error occurred while searching for users.", ephemeral=True, delete_after=10)

    async def select_specialization_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This interaction is not for you.", ephemeral=True, delete_after=10)
            return

        try:
            perk_specialization = self.perk_specialization_select.values[0]
            users_with_perks = self.db.get_users_with_perk_specialization(perk_specialization)
            if users_with_perks:
                embed = discord.Embed(title=f"Users with perks of specialization '{perk_specialization}'", color=discord.Color.purple())
                for user, perks in users_with_perks.items():
                    perks_list = '\n'.join([f"- {perk}" for perk in perks])
                    embed.add_field(name=user, value=perks_list, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(f"No users found with perks of specialization '{perk_specialization}'.", ephemeral=True, delete_after=5)
        except Exception as e:
            logger.error(f"Error processing perk search by specialization: {e}")
            await interaction.response.send_message("An error occurred while searching for users.", ephemeral=True, delete_after=10)

    async def open_name_input(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This interaction is not for you.", ephemeral=True)
            return

        modal = PerkNameInputModal(self.db, self.user_id)
        await interaction.response.send_modal(modal)

    async def view_all_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This interaction is not for you.", ephemeral=True, delete_after=10)
            return

        try:
            all_users_with_perks = self.db.get_all_users_with_perks()
            if all_users_with_perks:
                embed = discord.Embed(title="All users with their perks", color=discord.Color.gold())
                for user, perks in all_users_with_perks.items():
                    perks_list = '\n'.join([f"- {perk}" for perk in perks])
                    embed.add_field(name=user, value=perks_list, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("No users found with perks.", ephemeral=True, delete_after=5)
        except Exception as e:
            logger.error(f"Error processing view all users: {e}")
            await interaction.response.send_message("An error occurred while fetching all users with perks.", ephemeral=True, delete_after=10)

class ViewPerks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.command(name="viewperks", help="View perks of users")
    async def viewperks(self, ctx):
        try:
            view = PerkSearchView(self.db, ctx.author.id)
            await ctx.send("Select a search method and enter the required information:", view=view)
        except Exception as e:
            logger.error(f"Error in perk command: {e}")
            await ctx.send("An error occurred while setting up the search.")


def setup(bot):
    bot.add_cog(ViewPerks(bot))