import discord
from discord.ext import commands

import datetime as d

from bot import MultiSpoon

import newBDD
from utilities import dater as dat


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator

    return discord.app_commands.check(predicate)


@discord.app_commands.guild_only()
class RolesCog(commands.GroupCog, group_name="role"):
    def __init__(self, bot: MultiSpoon):
        self.bot = bot
        self.bot.tree.error(coro=self.bot.on_app_command_error)

    temp_group = discord.app_commands.Group(name="temporaire", description="meilleur_visibilité")

    # -----Commandes-----
    @temp_group.command(name="créer", description="Créer un rôle pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du rôle que vous voulez créer",
                                   couleur="La couleur du rôle que vous voulez")
    @is_admin()
    async def creer_role_temporaire(self, interaction: discord.Interaction, nom: str, couleur: str = "#99a9b5",separe: bool = False, mentionable: bool = False,
        jours: int = 0, heures: int = 0, minutes: int = 0, semaines: int = 0, mois: int = 0, annees: int = 0):
        if not jours and not heures and not minutes and not semaines and not mois and not annees :
            await interaction.response.send_message(
                embed=discord.Embed(title=":warning: Vous n'avez pas rentré de durée valide", color=discord.Colour.yellow()))
            return

        expiration = dat.get_expiration_time(minutes, heures, jours, semaines, mois, annees)

        if not dat.est_couleur_hexa(couleur):
            await interaction.channel.send(
                embed=discord.Embed(title=":warning: Vous n'avez pas rentré une couleur au format RGB ou RRGGBB"))
            return

        role = await interaction.guild.create_role(name=nom, colour=discord.Colour.from_str(couleur), hoist=separe,
                                                   mentionable=mentionable)

        await newBDD.addTempRole(role.id, interaction.guild_id, role.name, expiration.isoformat())
        await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le rôle a été crée", colour=discord.Color.green()))

    # @commands.hybrid_command(name="afficher", description="Affiche les salons temporaires crées")
    # async def afficher_salon_temporaire(self, ctx, salon: discord.abc.GuildChannel):
    #     embed = discord.Embed()
    #     channel = None
    #     for chan in self.bot.guilds_data[ctx.guild.name]["tempChannels"]:
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
    @temp_group.command(name="supprimer", description="Supprime un rôle temporaire crée")
    @discord.app_commands.describe(role="Le nom du rôle que vous voulez supprimer")
    @is_admin()
    async def supprimer_role_temporaire(self, interaction: discord.Interaction, role: discord.Role):
        suppr = False
        temp_role = await newBDD.getTempRole(role.id)
        if temp_role:
            await role.delete()
            await interaction.response.send_message(
                embed=discord.Embed(title=":white_check_mark: Le rôle temporaire a été supprimé",
                                        colour=0x008001))
            suppr = True

        if not suppr:
            await interaction.response.send_message(embed=discord.Embed(
                title=":warning: Le rôle que vous souhaitez supprimer n'existe pas ou n'est pas un rôle temporaire"))


async def setup(bot: MultiSpoon):
    await bot.add_cog(RolesCog(bot))
