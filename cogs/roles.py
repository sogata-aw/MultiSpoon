import discord
from discord.ext import commands

import datetime as d

from utilities import dater as dat

class RolesCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def is_admin():
        async def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.guild_permissions.administrator

        return discord.app_commands.check(predicate)

    @discord.app_commands.command(name="creer-role-temporaire", description="Créer un rôle pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du rôle que vous voulez créer",
                                   couleur="La couleur du rôle que vous voulez",
                                   duree="La durée que vous souhaitez mettre (voir /aide sur comment faire)")
    @is_admin()
    async def creerroletemporaire(self, interaction, nom: str, duree: str, couleur : str = "#99a9b5", separe : bool = False, mentionable : bool = False):
        if duree is None:
            await interaction.response.send_message(embed=discord.Embed(title=":warning: vous devez au moins rentrer une durée"))

        else:
            duree_de_base = d.datetime.now()

            duree_split = duree.split()
            total_duration = await dat.ajouter_temps(duree_split)
            if total_duration == duree_de_base:
                await interaction.response.send_message(embed=discord.Embed(title=":warning: Vous n'avez pas rentré de durée valide"))
            else:
                if dat.est_couleur_hexa(couleur):
                    await dat.create_role_duree(interaction, nom, total_duration, couleur, separe, mentionable, self.bot.settings)
                else:
                    await interaction.send(embed=discord.Embed(title=":warning: Vous n'avez pas rentré une couleur au format RGB ou RRGGBB"))

    # @commands.hybrid_command(name="affichersalontemporaire", description="Affiche les salons temporaires crées")
    # async def affichersalontemporaire(self, ctx, salon: discord.abc.GuildChannel):
    #     embed = discord.Embed()
    #     channel = None
    #     for chan in self.bot.settings["guilds"][ctx.guild.name]["tempChannels"]:
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
    @discord.app_commands.command(name="supprimer-role-temporaire", description="Supprime un salon temporaire crée")
    @discord.app_commands.describe()
    @is_admin()
    async def supprimersalontemporaire(self, interaction, nom: discord.Role):
        suppr = False
        for temp_role in self.bot.settings["guilds"][interaction.guild.name]["tempRoles"]:
            if temp_role["name"] == nom.name and temp_role["id"] == nom.id:
                role = interaction.guild.get_role(temp_role["id"])
                if role is None:
                    await interaction.response.send_message(
                        embed=discord.Embed(title=":warning: Le salon que vous souhaitez supprimer n'existe pas"))
                else:
                    await role.delete()
                    await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le salon temporaire a été supprimé",
                                                               colour=0x008001))
                    suppr = True
        if not suppr:
            await interaction.response.send_message(embed=discord.Embed(
                title=":warning: Le salon que vous souhaitez supprimer n'existe pas ou n'est pas un salon temporaire"))


async def setup(bot):
    await bot.add_cog(RolesCogs(bot))