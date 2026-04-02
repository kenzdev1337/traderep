import discord
from discord.ext import commands
from discord import app_commands, Embed

class Review(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    list = app_commands.Group(name="list", description="...")

    @app_commands.command(name="review", description="Donner un avis sur un échange")
    async def review(self, interaction:discord.Interaction):
        await interaction.response.send_message("Not implemented")

    @list.command(name="reviews", description="Voir les avis d'un membre")
    async def list_reviews(self, interaction:discord.Interaction, user:discord.User=None):
        if user == None:
            user = interaction.user
        await interaction.response.send_message("Not implemented")

async def setup(bot:commands.Bot):
    await bot.add_cog(Review(bot))