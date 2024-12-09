import typing
import datetime as d

import discord
from discord.ext import commands

from utilities import dater as dat


class SalonsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="creersalontemporaire", description="Créer un salon pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du salon que vous voulez créer",
                                   typesalon="Le type de salon que vous voulez créer",
                                   categorie="La catégorie dans lequel vous voulez créer le salon(dans aucune par défaut)",
                                   duree="La durée que vous souhaitez mettre (voir /aide sur comment faire)")
    @commands.has_permissions(administrator=True)
    async def creersalontemporaire(self, ctx, nom: str, typesalon: str, duree: str, categorie: discord.CategoryChannel = None):
        if duree is None:
            await ctx.send(embed=discord.Embed(title=":warning: vous devez au moins rentrer une durée"))

        else:
            duree_de_base = d.datetime.now()

            duree_split = duree.split()
            total_duration = await dat.ajouter_temps(duree_split)

            if total_duration == duree_de_base:
                await ctx.send(embed=discord.Embed(title=":warning: Vous n'avez pas rentré de durée valide"))
            else:
                await dat.create_channel_duree(ctx, nom, typesalon, self.bot.settings, categorie, total_duration)

    @commands.hybrid_command(name="affichersalontemporaire", description="Affiche les salons temporaires crées")
    async def affichersalontemporaire(self, ctx, salon = None, type : str = None):
        embed = discord.Embed()
        for i in range(len(self.bot.settings["guild"][ctx.guild.name]["tempChannels"])):
            if salon is not None :
                if salon == self.bot.settings["guild"][ctx.guild.name]["tempChannels"][i]["name"]:
                    embed.title = "Information sur le salon : " + self.bot.settings["guild"][ctx.guild.name]["tempChannels"][i]["name"]
                    for attribut in self.bot.settings["guild"][ctx.guild.name]["tempChannels"][i]:
                        if attribut == "duree":
                            embed.add_field(name="date d'expiration : " + self.bot.settings["guild"][ctx.guild.name]["tempChannels"][i][attribut], value="" , inline=False)
                        else:
                            embed.add_field(name=attribut + " : " +
                                        str(self.bot.settings["guild"][ctx.guild.name]["tempChannels"][i][attribut]), value="", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="supprimersalontemporaire", description="Supprime un salon temporaire crée")
    @discord.app_commands.describe()
    @commands.has_permissions(administrator=True)
    async def supprimersalontemporaire(self,ctx, nom : discord.abc.GuildChannel):
        suppr = False
        for chan in self.bot.settings["guild"][ctx.guild.name]["tempChannels"]:
            if chan["name"] == nom.name and chan["id"] == nom.id:
                channel = ctx.guild.get_channel(chan["id"])
                if channel is None:
                    await ctx.send(embed=discord.Embed(title=":warning: Le salon que vous souhaitez supprimer n'existe pas"))
                else:
                    await channel.delete()
                    await ctx.send(embed=discord.Embed(title=":white_check_mark: Le salon temporaire a été supprimé", colour=0x008001))
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





async def setup(bot):
    await bot.add_cog(SalonsCog(bot))