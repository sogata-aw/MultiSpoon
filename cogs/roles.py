import discord
from discord.ext import commands

import datetime as d

from bot import MultiSpoon

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
    @temp_group.command(name="creer", description="Créer un rôle pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du rôle que vous voulez créer",
                                   couleur="La couleur du rôle que vous voulez",
                                   duree="La durée que vous souhaitez mettre (voir /aide sur comment faire)")
    @is_admin()
    async def creer_role_temporaire(self, interaction: discord.Interaction, nom: str, duree: str, couleur: str = "#99a9b5",
                                    separe: bool = False, mentionable: bool = False):
        if duree is None:
            await interaction.response.send_message(
                embed=discord.Embed(title=":warning: vous devez au moins rentrer une durée"))

        else:
            duree_de_base = d.datetime.now()

            duree_split = duree.split()
            total_duration = await dat.ajouter_temps(duree_split)
            if total_duration == duree_de_base:
                await interaction.response.send_message(
                    embed=discord.Embed(title=":warning: Vous n'avez pas rentré de durée valide"))
            else:
                if dat.est_couleur_hexa(couleur):
                    await dat.create_role_duree(interaction, nom, total_duration, couleur, separe, mentionable,
                                                self.bot.guilds_data)
                else:
                    await interaction.channel.send(embed=discord.Embed(title=":warning: Vous n'avez pas rentré une couleur au format RGB ou RRGGBB"))

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
    @temp_group.command(name="supprimer", description="Supprime un salon temporaire crée")
    @discord.app_commands.describe(role="Le nom du rôle que vous voulez supprimer")
    @is_admin()
    async def supprimer_role_temporaire(self, interaction: discord.Interaction, role: discord.Role):
        suppr = False
        for temp_role in self.bot.guilds_data[interaction.guild.id].tempRoles:
            if temp_role.name == role.name and temp_role.id == role.id:
                role_to_del = interaction.guild.get_role(temp_role.id)
                if role_to_del is None:
                    await interaction.response.send_message(
                        embed=discord.Embed(title=":warning: Le salon que vous souhaitez supprimer n'existe pas"))
                else:
                    await role_to_del.delete()
                    await interaction.response.send_message(
                        embed=discord.Embed(title=":white_check_mark: Le salon temporaire a été supprimé",
                                            colour=0x008001))
                    suppr = True
        if not suppr:
            await interaction.response.send_message(embed=discord.Embed(
                title=":warning: Le salon que vous souhaitez supprimer n'existe pas ou n'est pas un salon temporaire"))


async def setup(bot: MultiSpoon):
    await bot.add_cog(RolesCog(bot))
