import discord
import os
import utils
import constants

from discord import app_commands, Embed
from discord.ext import commands

class Reputation(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.reputation_db = utils.Database(os.getenv("REP_USERNAME"), os.getenv("REP_PASSWORD"), os.getenv("REP_HOSTNAME"), os.getenv("REP_PORT"), os.getenv("REP_DB_NAME"))
        self.reviews_db = utils.Database(os.getenv("REVIEW_USERNAME"), os.getenv("REVIEW_PASSWORD"), os.getenv("REVIEW_HOSTNAME"), os.getenv("REVIEW_PORT"), os.getenv("REVIEW_DB_NAME"))
    
    @app_commands.command(name="reputation", description="Voir la réputation d'un membre")
    @app_commands.guild_only()
    async def reputation(self, interaction:discord.Interaction, user:discord.User=None):

        score_value = 0
        max_value = 0
        review_count_value = 0
        color = discord.Color.dark_gray()

        if user == None:
            user = interaction.user
        await interaction.response.defer()
        
        self.reputation_db.connect()
        self.reviews_db.connect()
        result = self.reputation_db.fetch(f"SELECT score FROM reputation WHERE user_id = {user.id}", 1)
        table_count = self.reviews_db.fetch(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{user.id}_reviews'", 1)
        
        if result == [] or table_count[0] == 0:
            if result == []:
                self.reputation_db.push(f"INSERT INTO reputation (user_id, score, max_value, review_count) VALUES ('{user.id}', '0', '0', '0')")
            embed = Embed(color=color, title=f"Réputation de {user.name}")
            embed.add_field(name="Score", value=score_value)
            embed.add_field(name="Avis", value="Cette personne n'a pas encore d'avis", inline=False)
            try:
                embed.set_thumbnail(url=user.avatar.url)
            except:
                pass
            await interaction.followup.send(embed=embed)
            return
        
        review_count = self.reviews_db.fetch(f"SELECT COUNT(*) FROM {user.id}_reviews", 1)
        score_value = result[0]

        last_review_count = self.reputation_db.fetch(f"SELECT review_count FROM reputation WHERE user_id = {user.id}", 1)

        data = self.reputation_db.fetch(f"SELECT max_value FROM reputation WHERE user_id = {user.id}", 1)
        max_value = data[0]
        review_count_value = review_count[0]

        if last_review_count[0] != review_count[0]:
            reviews = self.reviews_db.fetch_reviews(f"SELECT * FROM {user.id}_reviews")
            new_values = self.compute_score_max_value(reviews)
            self.reputation_db.push(f"UPDATE reputation SET score = {new_values[0]}, max_value = {new_values[1]}, review_count = {review_count[0]} WHERE user_id = {user.id}")
            score_value = new_values[0]
            max_value = new_values[1]

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
        embed.add_field(name="Valeur maximum d'échange", value=constants.VALUES[max_value])
        embed.add_field(name="Nombre d'avis", value=review_count_value)

        await interaction.followup.send(embed=embed)

    def compute_score_max_value(self, reviews):
        sum1 = 0
        sum2 = 0
        max_value = 0
        for review in reviews:
            if int(review[4]) == 1:
                sum1 += constants.POSITIVE_REVIEW_WEIGHT * int(review[4]) * int(review[3])
            elif int(review[4]) == -1:
                sum2 += constants.NEGATIVE_REVIEW_WEIGHT * int(review[4]) * int(review[3])

            if review[3] > max_value:
                max_value = review[3]
        finalsum = sum1 + sum2
        return finalsum, max_value


async def setup(bot:commands.Bot):
    await bot.add_cog(Reputation(bot))