import discord
from discord.ext import commands

import datetime as d
import traceback

from utilities import dater as dat

def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return discord.app_commands.check(predicate)

@discord.app_commands.guild_only()
class RolesCog(commands.GroupCog, group_name="role-temporaire"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.error(coro=self.on_app_command_error)

    temp_group = discord.app_commands.Group(name="temporaire", description="meilleur_visibilité")

    # -----Commandes-----
    async def on_app_command_error(self, interaction: discord.Interaction,
                                   error: discord.app_commands.AppCommandError):
        error_time = d.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        log_entry = (
            f"[{error_time}] ERREUR Slash Command (COG)\n"
            f"Auteur: {interaction.user} (ID: {interaction.user.id})\n"
            f"Guild: {interaction.guild} | Channel: {interaction.channel}\n"
            f"Erreur: {repr(error)}\n"
            f"Traceback:\n{tb}\n"
            f"{'-' * 60}\n"
        )
        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
        if interaction.response.is_done():
            await interaction.followup.send("❌ Une erreur est survenue (suivi).", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

    @temp_group.command(name="creer", description="Créer un rôle pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du rôle que vous voulez créer",
                                   couleur="La couleur du rôle que vous voulez",
                                   duree="La durée que vous souhaitez mettre (voir /aide sur comment faire)")
    @is_admin()
    async def creer_role_temporaire(self, interaction, nom: str, duree: str, couleur : str = "#99a9b5", separe : bool = False, mentionable : bool = False):
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
    @temp_group.command(name="supprimer", description="Supprime un salon temporaire crée")
    @discord.app_commands.describe(nom="Le nom du rôle que vous voulez supprimer")
    @is_admin()
    async def supprimer_role_temporaire(self, interaction, nom: discord.Role):
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
    await bot.add_cog(RolesCog(bot))