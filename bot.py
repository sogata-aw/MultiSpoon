import asyncio
import typing
import logging

import discord
from discord.ext import commands

import captcha as c
import settings as s

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Je suis prêt")
    for server in bot.guilds:
        print(f'{server.name}(id: {server.id})')
    print("Début de la synchronisation")
    await bot.tree.sync()
    print("Synchronisation terminée")
    commandes = bot.tree.get_commands()
    for command in commandes:
        print(f"Commande : {command.name}")
        print(f"Description : {command.description}")
        print("------------------------")


@bot.event
async def on_member_join(member):
    try:
        channel = member.guild.get_channel(settings["verificationChannel"])
        print(member.guild.get_role(settings["roleBefore"]))
        await member.add_roles(member.guild.get_role(settings["roleBefore"]))
        try:
            await channel.send(
                f"Bienvenue {member.mention} ! Veuillez utiliser la commande `/verify`")
        except discord.Forbidden:
            await channel.send(
                "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
    except AttributeError:
        await channel.send(":warning: Le bot ne trouve pas le rôle d'arrivée")


@bot.tree.command(name="setrole", description="Permet de configurer le rôle d'arrivée et celui après la vérification")
@discord.app_commands.describe(option = "Before : rôle à l'arrivée, After : rôle après vérification",role = "Le rôle que vous voulez sélectionner" )
@commands.has_permissions(administrator=True)
async def setrole(interaction, option: str, role: discord.Role):
    if option == "before":
        await s.set_role_before(interaction, role)
    elif option == "after":
        await s.set_role_after(interaction, role)
    await s.save()


@setrole.autocomplete("option")
async def autocomplete_option(interaction: discord.Interaction, option: str) -> typing.List[
    discord.app_commands.Choice[str]]:
    liste = []
    for choice in ["before", "after"]:
        liste.append(discord.app_commands.Choice(name=choice, value=choice))
    return liste


@bot.tree.command(name="setchannel",
                  description="Permet de configurer le salon ou sera envoyé le message quand quelqu'un arrive")
@discord.app_commands.describe(channel = "Le salon dans lequel vous voulez envoyer le message de bienvenue")
@commands.has_permissions(administrator=True)
async def setchannel(interaction, channel: discord.TextChannel):
    await s.set_verification_channel(interaction, channel)
    await s.save()


@bot.tree.command(name="settimeout", description="Permet de configurer le temps en seconde avant expiration du captcha")
@discord.app_commands.describe(time = "Le temps en secondes avant expiration de `/verify`")
@commands.has_permissions(administrator=True)
async def settimeout(interaction, time: int):
    await s.set_timeout(interaction, time)
    await s.save()



@bot.tree.command(name="aide", description="affiche les informations sur les différentes commandes")
async def aide(interaction: discord.Interaction, commande: str = None):
    roleBefore = interaction.guild.get_role(settings["roleBefore"])
    roleAfter = interaction.guild.get_role(settings["roleAfter"])
    logo = discord.File("logo.png", filename="logo.png")
    embed = discord.Embed(title="Commande disponible",
                          description="Affiche la description de toutes les commandes disponibles")
    embed.set_thumbnail(url="attachment://logo.png")
    embed.add_field(name="setrole",
                    value="Configure le rôle choisi par l'utilisateur avec les paramètres before(rôle à l'arrivée) et after(rôle après captcha)",
                    inline=True)
    embed.add_field(name="setchannel",
                    value="Configure le salon ou seront envoyés les messages de bienvenue incitant à utiliser la commande `/verify`",
                    inline=True)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="settimeout", value="Configure le temps avant expiration de la commande `/verify`",
                    inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="verify",
                    value=f"Commande utilisé par les personnes possédant le rôle {roleBefore.mention} et d'obtenir le rôle {roleAfter.mention}")
    embed.set_footer(text=f"Informations demandées par : {interaction.user.display_name}")
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name=" ", value=" ", inline=False)
    embed.add_field(name="afficher", value="affiche les différents paramètres du bot", inline=True)
    embed.add_field(name="aide", value="affiche les commandes disponibles pour le bot")
    await interaction.response.send_message(file=logo, embed=embed)


@bot.tree.command(name="afficher",
                  description="Affiche les différents paramètres mis en place (admin uniquement)")  # à améliorer
@commands.has_permissions(administrator=True)
async def afficher(interaction):
    out = ""
    for key in settings:
        if not key == "token":
            out += (f"{key} : {settings[key]}\n")
    await interaction.response.send_message(f"Voici les différents paramètres :\n{out}")


@bot.tree.command(name="verify", description="Permet de lancer la vérification")
async def verify(interaction: discord.Interaction):
    if not (interaction.guild.get_role(settings["roleBefore"]) in interaction.user.roles):
        await interaction.response.send_message(":warning: Vous avez déjà effectué la vérification")
    elif settings["verificationChannel"] == 0 or settings["roleBefore"] == 0 or settings["roleAfter"] == 0:
        await interaction.response.send_message(
            ":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation"
        )
    else:
        continuer = True
        tmps = settings["timeout"] / 60
        nb = settings["nbEssais"]
        while continuer:
            code = c.generer_code()
            print(code)
            c.creer_captcha(code)
            attachement = discord.File("captcha.png", filename="captcha.png")
            await interaction.response.send_message(
                f"Veuillez rentrer le code du captcha, vous avez {int(tmps)} minutes pour le faire et {nb} avant de devoir contacter un administrateur ",
                file=attachement)

            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel

            try:
                reponse = await bot.wait_for('message', check=check, timeout=settings["timeout"])
            except TimeoutError:
                interaction.channel.send("Temps écoulé ! Veuillez recommencer")

            # Agir en fonction de la réponse de l'utilisateur
            if reponse.content == code:
                await interaction.channel.send(f"Le code est bon ! Bienvenue sur {interaction.guild.name}")
                await interaction.user.add_roles(interaction.guild.get_role(settings["roleAfter"]))
                asyncio.sleep(0.5)
                await interaction.user.remove_roles(interaction.guild.get_role(settings["roleBefore"]))
                continuer = False

                await interaction.channel.purge()
            else:
                await interaction.channel.send("Code incorrect... Veuillez recommencer.")
                await interaction.channel.purge()


def run():
    bot.run(settings["token"])


if __name__ == "__main__":
    settings = s.loading()
    run()
