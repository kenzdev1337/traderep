import discord
import os

from discord import app_commands, Embed
from discord.ext import commands

class Review(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="reputation", description="Voir la réputation d'un membre")
    async def reputation(self, interaction:discord.Interaction, user:discord.User=None):
        if user == None:
            user = interaction.user
        await interaction.response.send_message("Not implemented")