import typing

import discord
from discord.ext import commands

from utilities import dater as d


class SalonsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="creersalontemporaire", description="Créer un salon pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du salon que vous voulez créer",
                                   typesalon="Le type de salon que vous voulez créer",
                                   categorie="La catégorie dans lequel vous voulez créer le salon(dans aucune par défaut)",
                                   duree="La durée que vous souhaitez mettre (voir /aide sur comment faire)")
    @commands.has_permissions(administrator=True)
    async def creersalontemporaire(self, ctx, nom: str, typesalon: str, duree: str, categorie: str = None):
        cat = None
        for category in ctx.guild.categories:
            if category.name == categorie:
                cat = category
        await d.verif_format_channel(ctx, nom, typesalon, self.bot.settings, cat, duree)

    @commands.hybrid_command(name="affichersalontemporaire", description="Affiche les salons temporaires crées")
    async def affichersalontemporaire(self, ctx, salon = None):
        pass

    @commands.hybrid_command(name="supprimersalontemporaire", description="Supprime un salon temporaire crée")
    @discord.app_commands.describe()
    @commands.has_permissions(administrator=True)
    async def supprimersalontemporaire(self,ctx, nom : str):
        suppr = False
        for chan in self.bot.settings[ctx.guild.name]["tempChannels"]:
            if chan["name"] == nom:
                channel = ctx.guild.get_channel(chan["id"])
                if channel is None:
                    await ctx.send(embed=discord.Embed(title=":warning: Le salon que vous souhaitez supprimer n'existe pas"))
                else:
                    await channel.delete()
                    await ctx.send(embed=discord.Embed(title=":white_check_mark: Le salon temporaire a été supprimé"))
                    suppr = True
        if not suppr:
            await ctx.send(embed=discord.Embed(title=":warning: Le salon que vous souhaitez supprimer n'existe pas ou n'est pas un salon temporaire"))



    # -----Autocomplete-----

    # creersalontemporaire
    @creersalontemporaire.autocomplete("typesalon")
    async def autocomplete_type(self, ctx, typesalon: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["textuel", "vocal"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste

    @creersalontemporaire.autocomplete("categorie")
    async def autocomplete_category(self, ctx, categorie: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for category in ctx.guild.categories:
            liste.append(discord.app_commands.Choice(name=category.name, value=category.name))
        return liste

    # supprimersalontemporaire
    @supprimersalontemporaire.autocomplete("nom")
    async def autocomplete_nom(self, ctx, nom: str) -> typing.List[discord.app_commands.Choice[str]]:
        liste = []
        for chan in self.bot.settings[ctx.guild.name]["tempChannels"]:
            liste.append(discord.app_commands.Choice(name=chan["name"], value=chan["name"]))
        return liste

async def setup(bot):
    await bot.add_cog(SalonsCog(bot))