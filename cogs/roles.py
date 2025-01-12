import discord
from discord.ext import commands

import datetime as d

from utilities import dater as dat

class RolesCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="creerroletemporaire", description="Créer un rôle pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du rôle que vous voulez créer",
                                   couleur="La couleur du rôle que vous voulez",
                                   duree="La durée que vous souhaitez mettre (voir /aide sur comment faire)")
    @commands.has_permissions(administrator=True)
    async def creerroletemporaire(self, ctx, nom: str, duree: str, couleur : str = "#99a9b5",separe : bool = False, mentionable : bool = False):
        if duree is None:
            await ctx.send(embed=discord.Embed(title=":warning: vous devez au moins rentrer une durée"))

        else:
            duree_de_base = d.datetime.now()

            duree_split = duree.split()
            total_duration = await dat.ajouter_temps(duree_split)
            if total_duration == duree_de_base:
                await ctx.send(embed=discord.Embed(title=":warning: Vous n'avez pas rentré de durée valide"))
            else:
                if dat.est_couleur_hexa(couleur):
                    await dat.create_role_duree(ctx, nom, total_duration, couleur, separe, mentionable, self.bot.settings)
                else:
                    await ctx.send(embed=discord.Embed(title=":warning: Vous n'avez pas rentré une couleur au format RGB ou RRGGBB"))

    # @commands.hybrid_command(name="affichersalontemporaire", description="Affiche les salons temporaires crées")
    # async def affichersalontemporaire(self, ctx, salon: discord.abc.GuildChannel):
    #     embed = discord.Embed()
    #     channel = None
    #     for chan in self.bot.settings["guild"][ctx.guild.name]["tempChannels"]:
    #         if salon.id == chan["id"]:
    #             channel = chan
    #     if channel is None:
    #         embed.title = ":warning: Le salon , n'est pas valide ou n'est pas un salon temporaire"
    #     else:
    #         embed.title = "Information sur le salon : " + channel["name"]
    #         for attribut in channel:
    #             if attribut == "duree":
    #                 embed.add_field(name="date d'expiration : " +
    #                                      channel[attribut], value="", inline=False)
    #             else:
    #                 embed.add_field(name=attribut + " : " +
    #                                      str(channel[attribut]), value="", inline=False)
    #     await ctx.send(embed=embed)
    #
    @commands.hybrid_command(name="supprimerroletemporaire", description="Supprime un salon temporaire crée")
    @discord.app_commands.describe()
    @commands.has_permissions(administrator=True)
    async def supprimersalontemporaire(self, ctx, nom: discord.Role):
        suppr = False
        for rolee in self.bot.settings["guild"][ctx.guild.name]["tempRoles"]:
            if rolee["name"] == nom.name and rolee["id"] == nom.id:
                role = ctx.guild.get_role(rolee["id"])
                if role is None:
                    await ctx.send(
                        embed=discord.Embed(title=":warning: Le salon que vous souhaitez supprimer n'existe pas"))
                else:
                    await role.delete()
                    await ctx.send(embed=discord.Embed(title=":white_check_mark: Le salon temporaire a été supprimé",
                                                       colour=0x008001))
                    suppr = True
        if not suppr:
            await ctx.send(embed=discord.Embed(
                title=":warning: Le salon que vous souhaitez supprimer n'existe pas ou n'est pas un salon temporaire"))


async def setup(bot):
    await bot.add_cog(RolesCogs(bot))