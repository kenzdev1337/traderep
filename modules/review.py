import discord
import utils
import os

from discord.ext import commands
from discord import app_commands, Embed

class Review(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.reviews_db = utils.Database(os.getenv("REVIEW_USERNAME"), os.getenv("REVIEW_PASSWORD"), os.getenv("REVIEW_HOSTNAME"), os.getenv("REVIEW_PORT"), os.getenv("REVIEW_DB_NAME"))

    list = app_commands.Group(name="list", description="...")

    @app_commands.command(name="review", description="Donner un avis sur un échange")
    async def review(self, interaction:discord.Interaction, user:discord.User):
        if user == interaction.user:
            await interaction.response.send_message("Vous ne pouvez pas laisser d'avis à vous-même")
            return
        if user.bot :
            await interaction.response.send_message("Vous ne pouvez évaluer que des utilisateur")
            return
        
        view = CustomView()
        modal = ReviewModal(user)
        await interaction.response.send_modal(modal)
        await modal.wait()

        review_text = modal.value

        await interaction.followup.send(view=view, ephemeral=True)
        await view.wait()

        trade_value = view.trade_value
        experience = view.experience

        self.reviews_db.connect()
        table_name = f"{user.id}_reviews"
        result = self.reviews_db.fetchall("SHOW TABLES")
        table_count = 0
        for name in result:
            if name == table_name:
                table_count += 1
        if table_count == 0:
            self.reviews_db.execute(f"CREATE TABLE {user.id}_reviews (id INT(10) NOT NULL AUTO_INCREMENT, review_text VARCHAR(255), user_id BIGINT(20), trade_value INT(1), experience INT(1), PRIMARY KEY(id))")
        self.reviews_db.push(f"INSERT INTO {user.id}_reviews (review_text, user_id, trade_value, experience) VALUES ('{review_text}', '{interaction.user.id}', '{trade_value}', '{experience}')")

        await interaction.followup.send(content=f"Avis donné à {user.mention}", ephemeral=True)

    @list.command(name="reviews", description="Voir les avis d'un membre")
    async def list_reviews(self, interaction:discord.Interaction, user:discord.User=None):
        if user == None:
            user = interaction.user
        await interaction.response.send_message("Not implemented")

async def setup(bot:commands.Bot):
    await bot.add_cog(Review(bot))

#Classes UI

class CustomView(discord.ui.View):
    def __init__(self):
        self.trade_value = None
        self.experience = None
        self.editable = True
        super().__init__()

    trade_values_options = [
            discord.SelectOption(label="0-100€", value=0),
            discord.SelectOption(label="100-500€", value=1),
            discord.SelectOption(label="500-1000€", value=2),
            discord.SelectOption(label="1000+€", value=3)
    ]

    experience_options = [
        discord.SelectOption(label="Bonne", value=1, emoji="✅"),
        discord.SelectOption(label="Mauvaise", value=-1, emoji="❌")
    ]
    
    @discord.ui.select(placeholder="Indiquez la valeur de l'échange", min_values=1, max_values=1, options=trade_values_options)
    async def trade_value_select(self, interaction:discord.Interaction, select:discord.ui.Select):
        self.trade_value = self.trade_value_select.values[0]
        await interaction.response.defer()

    @discord.ui.select(placeholder="Votre expérience fut-elle...", min_values=1, max_values=1, options=experience_options)
    async def experience_select(self, interaction:discord.Interaction, select:discord.ui.Select):
        self.experience = self.experience_select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="Confirmer", emoji="✅", style=discord.ButtonStyle.green)
    async def confirm(self, interaction:discord.Interaction, button:discord.ui.Button):
        if self.trade_value != None and self.experience != None:
            self.stop()
        await interaction.response.defer()
    
class ReviewModal(discord.ui.Modal, title="Avis"):
    def __init__(self, user:discord.User):
        self.user = user
        self.value = None
        super().__init__()

    review = discord.ui.TextInput(placeholder="Votre avis...", required=True, max_length=150, label="Votre avis (max. 150 caractères)")

    async def on_submit(self, interaction:discord.Interaction):
        self.value = self.review.value
        await interaction.response.defer()
