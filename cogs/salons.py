import typing
import datetime as d
import traceback

import discord
from discord.ext import commands

from utilities import dater as dat

def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return discord.app_commands.check(predicate)

@discord.app_commands.guild_only()
class SalonsCog(commands.GroupCog, group_name="salon"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.error(coro=self.on_app_command_error)

    temp_group = discord.app_commands.Group(name="temporaire", description="meilleur_visibilité")

    # -----Commandes-----

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
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

    @temp_group.command(name="creer", description="Créer un salon pour une durée déterminée")
    @discord.app_commands.describe(nom="Le nom du salon que vous voulez créer",
                                   typesalon="Le type de salon que vous voulez créer",
                                   categorie="La catégorie dans lequel vous voulez créer le salon(dans aucune par défaut)",
                                   duree="La durée que vous souhaitez mettre (voir /aide sur comment faire)")
    @is_admin()
    async def creer_salon_temporaire(self, interaction, nom: str, typesalon: str, duree: str,
                                   categorie: discord.CategoryChannel = None):
        if duree is None:
            await interaction.response.send_message(embed=discord.Embed(title=":warning: vous devez au moins rentrer une durée"))

        else:
            duree_de_base = d.datetime.now()

            duree_split = duree.split()
            total_duration = await dat.ajouter_temps(duree_split)

            if total_duration == duree_de_base:
                await interaction.response.send_message(embed=discord.Embed(title=":warning: Vous n'avez pas rentré de durée valide"))
            else:
                await dat.create_channel_duree(interaction, nom, typesalon, self.bot.guilds_data, categorie, total_duration)

    # @temp_group.command(name="afficher", description="Affiche les salons temporaires crées")
    # async def afficher_salon_temporaire(self, interaction, salon: discord.abc.GuildChannel):
    #     embed = discord.Embed()
    #     channel = None
    #     for chan in self.bot.guilds_data[interaction.guild.name].tempChannels:
    #         if salon.id == chan.id:
    #             channel = chan
    #     if channel is None:
    #         embed.title = ":warning: Le salon , n'est pas valide ou n'est pas un salon temporaire"
    #     else:
    #         embed.title = "Information sur le salon : " + channel.name
    #         for attribut in channel:
    #             print(type(attribut[0]))
    #             print(type(attribut[1]))
    #             if attribut == "duree":
    #                 embed.add_field(name="date d'expiration : " +
    #                                      eval('channel.attribut[0]'), value="", inline=False)
    #             else:
    #                 embed.add_field(name=attribut[0] + " : " +
    #                                      str(channel[attribut[0]]), value="", inline=False)
    #     await interaction.response.send_message(embed=embed)

    @temp_group.command(name="supprimer", description="Supprime un salon temporaire crée")
    @discord.app_commands.describe(nom="Le nom du salon que vous voulez supprimer")
    @is_admin()
    async def supprimer_salon_temporaire(self, interaction, nom: discord.abc.GuildChannel):
        suppr = False
        for temp_channel in self.bot.guilds_data[interaction.guild.name].tempChannels:
            if temp_channel.name == nom.name and temp_channel.id == nom.id:
                channel = interaction.guild.get_channel(temp_channel.id)
                if channel is None:
                    await interaction.response.send_message(
                        embed=discord.Embed(title=":warning: Le salon que vous souhaitez supprimer n'existe pas"))
                else:
                    await channel.delete()
                    await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Le salon temporaire a été supprimé",
                                                               colour=0x008001))
                    suppr = True
        if not suppr:
            await interaction.response.send_message(embed=discord.Embed(
                title=":warning: Le salon que vous souhaitez supprimer n'existe pas ou n'est pas un salon temporaire"))

    # -----Autocomplete-----

    # creersalontemporaire
    @creer_salon_temporaire.autocomplete("typesalon")
    async def autocomplete_type(self, interaction, typesalon: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["textuel", "vocal"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste


async def setup(bot):
    await bot.add_cog(SalonsCog(bot))
