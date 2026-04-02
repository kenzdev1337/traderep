import discord
import os
import utils

from discord import app_commands, Embed
from discord.ext import commands

class Reputation(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="reputation", description="Voir la réputation d'un membre")
    async def reputation(self, interaction:discord.Interaction, user:discord.User=None):
        if user == None:
            user = interaction.user
        await interaction.response.defer()

        reputation_db = utils.Databse(os.getenv("REP_USERNAME"), os.getenv("REP_PASSWORD"), os.getenv("REP_HOSTNAME", os.getenv("REP_PORT")))
        reputation_db.connect()

        score_value = None
        color = discord.Color.dark_gray()

        if score_value > 0:
            color = discord.Color.green()
        elif score_value < 0:
            color = discord.Color.red()

        embed = Embed(color=color, title=f"Réputation de {user.global_name}")
        embed.add_field(name="Score", value=score_value)

        await interaction.followup.send("Not implemented")

async def setup(bot):
    await bot.add_cog(Reputation(bot))