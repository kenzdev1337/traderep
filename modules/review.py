import discord
import utils
import os
import math

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
        
        view = ReviewView()
        modal = ReviewModal(user)
        await interaction.response.send_modal(modal)
        await modal.wait()

        review_text = modal.value

        await interaction.followup.send(view=view, ephemeral=True)
        await view.wait()

        trade_value = view.trade_value
        experience = view.experience

        self.reviews_db.connect()
        table_count = self.reviews_db.fetch(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{user.id}_reviews'", 1)
        if table_count[0] == 0:
            self.reviews_db.execute(f"CREATE TABLE {user.id}_reviews (id INT(10) NOT NULL AUTO_INCREMENT, review_text VARCHAR(255), user_id BIGINT(20), trade_value INT(1), experience INT(1), PRIMARY KEY(id))")
        self.reviews_db.push(f"INSERT INTO {user.id}_reviews (review_text, user_id, trade_value, experience) VALUES ('{review_text}', '{interaction.user.id}', '{trade_value}', '{experience}')")

        await interaction.followup.send(content=f"Avis donné à {user.mention}", ephemeral=True)

    @list.command(name="reviews", description="Voir les avis d'un membre")
    async def list_reviews(self, interaction:discord.Interaction, user:discord.User=None):
        if user == None:
            user = interaction.user
        if user.bot:
            await interaction.response.send_message("Vous ne pouvez voir que les avis des utilisateurs")
            return

        currentpage = 0

        result = self.list_logic(user, currentpage)
        view = PageView(currentpage, result[1])

        while True:
            result = self.list_logic(user, currentpage)
            view = PageView(currentpage, result[1])
            try:
                await interaction.response.send_message(embed=result[0], view=view)
            except:
                msg = await interaction.original_response()
                await msg.edit(embed=result[0], view=view)
            await view.wait()
            currentpage = view.current_page

    def list_logic(self, user:discord.User, currentpage:int):
        pagecount = 0
        currentpage = currentpage
        max = 0
        
        self.reviews_db.connect()
        table_count = self.reviews_db.fetch(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{user.id}_reviews'", 1)
        if table_count[0] == 0:
            embed = discord.Embed(title=f"Avis de {user.name}")
            embed.add_field(name="Pas encore d'avis", value="Cet utilisateur n'a pas encore d'avis")
        else:
            count = self.reviews_db.fetch(f"SELECT COUNT(*) FROM {user.id}_reviews", 1)
            if count[0] % 10 == 0:
                pagecount = count[0] / 10
            else:
                pagecount = math.floor(count[0] / 10) + 1
            reviews = self.reviews_db.fetch_reviews(f"SELECT * FROM {user.id}_reviews")
            embed = discord.Embed(title=f"Avis de {user.name}", description=f"Page {currentpage+1}/{pagecount}")
            if 10*currentpage+10 > count[0]:
                max = count[0]
            else:
                max = 10*currentpage+10
            for i in range(10*currentpage, max):
                experience = 0
                if reviews[i][4] == -1:
                    experience = "Négatif ❌"
                else:
                    experience = "Positif ✅"
                embed.add_field(name=experience, value=reviews[i][1], inline=False)
        return embed, pagecount-1
        

async def setup(bot:commands.Bot):
    await bot.add_cog(Review(bot))

#Classes UI

#Interface infos supplémentaires
class ReviewView(discord.ui.View):
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

#Modal
class ReviewModal(discord.ui.Modal, title="Avis"):
    def __init__(self, user:discord.User):
        self.user = user
        self.value = None
        super().__init__()

    review = discord.ui.TextInput(placeholder="Votre avis...", required=True, max_length=150, label="Votre avis (max. 150 caractères)")

    async def on_submit(self, interaction:discord.Interaction):
        self.value = self.review.value
        await interaction.response.defer()

class PageView(discord.ui.View):
    def __init__(self, currentpage:int, max_pages:int):
        self.current_page = currentpage
        self.max_pages = max_pages
        super().__init__()

    @discord.ui.button(label="Page précédente", emoji="⏪")
    async def previous_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if self.current_page-1 < 0:
            await interaction.response.send_message("Pas de page supplémentaire à afficher", ephemeral=True)
            return
        self.current_page -= 1
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Page suivante", emoji="⏩")
    async def next_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        if self.current_page+1 > self.max_pages:
            await interaction.response.send_message("Pas de page supplémentaire à afficher", ephemeral=True)
            return
        self.current_page += 1
        self.stop()
        await interaction.response.defer()