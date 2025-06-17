import typing
import asyncio
import os

import discord
from discord.ext import commands

from view.aideView import AideSelectView
from utilities import captchas as c, settings as s
from utilities import embeds as e


def is_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return discord.app_commands.check(predicate)

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----Commandes-----

    @discord.app_commands.command(name="aide", description="affiche les informations sur les différentes commandes")
    async def aide(self, interaction, commande: str = None):
        if commande is None:
            embed = discord.Embed(title="Choisissez une catégorie")
            await interaction.response.send_message(embed=embed, view=AideSelectView())

        elif commande == "music":
            await interaction.response.send_message(embed=await e.embed_aide(commande, self.bot.settings["commands"]["music"]),
                                   view=AideSelectView())

        elif commande == "moderation":
            await interaction.response.send_message(embed=await e.embed_aide(commande, self.bot.settings["commands"]["music"]),
                                   view=AideSelectView())

    @discord.app_commands.command(name="settings",
                             description="Affiche les différents paramètres mis en place (admin uniquement)")  # à améliorer
    @is_admin()
    @discord.app_commands.guild_only()
    async def settings(self, interaction):

        salon = interaction.guild.get_channel(self.bot.settings["guilds"][interaction.guild.name]["verificationChannel"])
        role_before = interaction.guild.get_role(self.bot.settings["guilds"][interaction.guild.name]["roleBefore"])
        role_after = interaction.guild.get_role(self.bot.settings["guilds"][interaction.guild.name]["roleAfter"])

        embed = discord.Embed(title="paramètre du bot :")
        embed.add_field(name="Salon de vérification : ", value=salon.mention)
        embed.add_field(name="Rôle d'arrivée : ", value=role_before.mention)
        embed.add_field(name="Rôle après vérification : ", value=role_after.mention)
        embed.add_field(name="Temps de la commande vérification : ",
                        value=self.bot.settings["guilds"][interaction.guild.name]["timeout"])
        embed.add_field(name="Nombre d'essais : ", value=self.bot.settings["guilds"][interaction.guild.name]["nbEssais"])

        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="sync", description="Synchronise toutes les personnes qui ont le rôle après vérification")
    @is_admin()
    @discord.app_commands.guild_only()
    async def sync(self, interaction):
        for member in interaction.guild.members:
            if member.id not in self.bot.settings["guilds"][interaction.guild.name]["alreadyVerified"] and member.get_role(self.bot.settings["guilds"][interaction.guild.name]["roleAfter"]) != None :
                self.bot.settings["guilds"][interaction.guild.name]["alreadyVerified"].append(member.id)
        await interaction.response.send_message("Synchronisation terminé !")


    @discord.app_commands.command(name="verify", description="Permet de lancer la vérification")
    @discord.app_commands.guild_only()
    async def verify(self, interaction):
        reponse = None
        if not (interaction.guild.get_role(self.bot.settings["guilds"][interaction.guild.name]["roleBefore"]) in interaction.user.roles):
            await interaction.response.send_message(":warning: Vous avez déjà effectué la vérification")

        elif interaction.user.name in self.bot.settings["guilds"][interaction.guild.name]["inVerification"]:
            await interaction.response.send_message(":warning: Vous êtes déjà en train de faire une vérification ! si vous avez raté le code donnée, attendez que le bot regénère un code")

        elif self.bot.settings["guilds"][interaction.guild.name]["verificationChannel"] == 0 or \
                self.bot.settings["guilds"][interaction.guild.name][
                    "roleBefore"] == 0 or self.bot.settings["guilds"][interaction.guild.name]["roleAfter"] == 0:

            await interaction.response.send_message(
                ":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation"
            )
        else:
            self.bot.settings["guilds"][interaction.guild.name]["inVerification"].append(interaction.user.name)
            continuer = True
            tmps = self.bot.settings["guilds"][interaction.guild.name]["timeout"] / 60
            first = True

            while continuer:
                code = c.generer_code()
                c.generer_image(code)
                attachement = discord.File("img/captcha.png", filename="img/captcha.png")

                if first :
                    await interaction.response.send_message(
                        f"{interaction.user.name} veuillez rentrer le code du captcha **en minuscule**, vous avez {int(tmps)} minutes pour le faire",
                        file=attachement)
                    first = False
                else :
                    await interaction.channel.send(
                        f"{interaction.user.name} veuillez rentrer le code du captcha **en minuscule**, vous avez {int(tmps)} minutes pour le faire",
                        file=attachement)

                def verify_check(msg):
                    return msg.author == interaction.user and msg.channel == interaction.channel

                def msg_check(msg):
                    return (msg.author == interaction.user
                            or (interaction.client.user == msg.author
                                and (interaction.user.name.lower() in msg.content.lower()
                                     or msg.content.lower() == f"Le code est bon ! Bienvenue sur {interaction.guild.name}".lower()
                                     or msg.content.lower() == "Code incorrect... Veuillez recommencer.".lower())))

                try:
                    reponse = await self.bot.wait_for('message', check=verify_check,
                                                      timeout=self.bot.settings["guilds"][interaction.guild.name]["timeout"])

                    # Agir en fonction de la réponse de l'utilisateur
                    if reponse.content == code:
                        self.bot.settings["guilds"][interaction.guild.name]["inVerification"].remove(interaction.user.name)

                        await interaction.channel.send(f"Le code est bon ! Bienvenue sur {interaction.guild.name}")
                        await interaction.user.add_roles(
                            interaction.guild.get_role(self.bot.settings["guilds"][interaction.guild.name]["roleAfter"]))

                        await asyncio.sleep(0.5)

                        await interaction.user.remove_roles(
                            interaction.guild.get_role(self.bot.settings["guilds"][interaction.guild.name]["roleBefore"]))
                        continuer = False

                        self.bot.settings["guilds"][interaction.guild.name]["alreadyVerified"].append(interaction.user.id)
                        await interaction.channel.purge(limit=50, check=msg_check)

                    else:
                        await interaction.channel.send("Code incorrect... Veuillez recommencer.")
                        await asyncio.sleep(0.5)
                        await interaction.channel.purge(limit=50, check=msg_check)

                except asyncio.TimeoutError:
                    self.bot.settings["guilds"][interaction.guild.name]["inVerification"].remove(interaction.user.name)


    # -----autocomplete-----

    # Aide

    @aide.autocomplete("commande")
    async def autocomplete_commande(self, interaction, commande: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for cat in self.bot.settings["commands"]:
            liste.append(discord.app_commands.Choice(name=cat, value=cat))

        return liste


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
