import typing
import asyncio
import os
import datetime
import traceback

import discord
from discord.ext import commands

def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return discord.app_commands.check(predicate)

class VoiceChannelCogs(commands.GroupCog, group_name="vocal"):
    def __init__(self, bot):
        self.bot = bot

        self.bot.tree.error(coro=self.on_app_command_error)

        # -----Commandes-----

    async def on_app_command_error(self, interaction: discord.Interaction,
                                       error: discord.app_commands.AppCommandError):
            error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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


    temp_group = discord.app_commands.Group(name="temporaire", description="meilleur_visibilité")


    @temp_group.command(name="ajouter", description="Permet d'ajouter un déclencheur sur un vocal pour créer des vocaux temporaires")
    @discord.app_commands.describe(salon="Sélectionnez le vocal pour lequelle vous voulez ajouter un déclencheur")
    @is_admin()
    async def ajouter(self, interaction : discord.Interaction, salon : discord.VoiceChannel):
        self.bot.guilds_data[interaction.guild.name].channelToCheck.append(salon.id)
        await interaction.response.send_message(embed=discord.Embed(colour=discord.Colour.from_str("#68cd67"), title=":white_check_mark: Le salon a été ajouté à la liste des salons déclencheurs."))

    @temp_group.command(name="créer", description="Permet de créer vocal avec un déclencheur permettant d'en créer des temporaires")
    @discord.app_commands.describe(nom="Choisissez le nom de votre nouveau salon",
                                   capacite="Choisissez votre capacité maximum de votre nouveau salon (max. 99)",
                                   categorie="Sélectionnez dans quelle catégorie votre nouveau salon sera crée")
    @is_admin()
    async def creer(self, interaction : discord.Interaction, nom : str = None , capacite : int = None , categorie  : discord.CategoryChannel = None):
        channel = await interaction.guild.create_voice_channel(name=nom, category=categorie, user_limit=capacite)
        self.bot.guilds_data[interaction.guild.name].channelToCheck.append(channel.id)
        await interaction.response.send_message(embed=discord.Embed(colour=discord.Colour.from_str("#68cd67"), title=":white_check_mark: Le salon a été ajouté à la liste des salons déclencheurs."))

    @temp_group.command(name="supprimer", description="Supprime l'écoute d'un salon permettant d'en créer des temporaires")
    @is_admin()
    async def supprimer(self, interaction : discord.Interaction, salon : discord.VoiceChannel):
        if salon.id in self.bot.guilds_data[interaction.guild.name].channelToCheck:
            self.bot.guilds_data[interaction.guild.name].channelToCheck.remove(salon.id)
            await interaction.response.send_message(embed=discord.Embed(colour=discord.Colour.from_str("#68cd67"), title=":white_check_mark: Ce salon ne déclenchera plus la création automatique de salons vocaux."))
        else:
            await interaction.response.send_message(embed=discord.Embed(colour=discord.Color.red(), title=":warning: Ce salon n'est pas configuré pour la création automatique de salons vocaux temporaires."))

    @temp_group.command(name="afficher", description="affiche les vocaux qui possède un déclencheur pour créer des salons temporaires")
    async def afficher(self, interaction : discord.Interaction):
        embed = discord.Embed(title="Liste des salons vocaux avec un déclencheur", description="Cliquez sur un vocal pour le rejoindre")
        for vocal in self.bot.guilds_data[interaction.guild.name].channelToCheck :
            embed.add_field(name=f"{interaction.guild.get_channel(vocal).mention}", value="")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(VoiceChannelCogs(bot))