import discord
import os
import utils

from discord import app_commands, Embed
from discord.ext import commands

class Reputation(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="reputation", description="Voir la réputation d'un membre")
    @app_commands.guild_only()
    async def reputation(self, interaction:discord.Interaction, user:discord.User=None):

        score_value = 0
        color = discord.Color.dark_gray()

        if user == None:
            user = interaction.user
        await interaction.response.defer()

        reputation_db = utils.Database(os.getenv("REP_USERNAME"), os.getenv("REP_PASSWORD"), os.getenv("REP_HOSTNAME"), os.getenv("REP_PORT"), os.getenv("REP_DB_NAME"))
        reputation_db.connect()
        result = reputation_db.fetch(f"SELECT score FROM reputation WHERE user_id = {user.id}", 1)

        if result == []:
            embed = Embed(color=color, title=f"Réputation de {user.name}")
            embed.add_field(name="Score", value=score_value)
            embed.add_field(name="Avis", value="Cette personne n'a pas encore d'avis", inline=False)
            try:
                embed.set_thumbnail(url=user.avatar.url)
            except:
                pass
            await interaction.followup.send(embed=embed)
            return

        score_value = result[0]
        print(score_value)
        color = discord.Color.dark_gray()

        if score_value > 0:
            color = discord.Color.green()
        elif score_value < 0:
            color = discord.Color.red()
        
        embed = Embed(color=color, title=f"Réputation de {user.name}")
        try:
            embed.set_thumbnail(url=user.avatar.url)
        except:
            pass
        embed.add_field(name="Score", value=score_value)

        await interaction.followup.send(embed=embed)

async def setup(bot:commands.Bot):
    await bot.add_cog(Reputation(bot))