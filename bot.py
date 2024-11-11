import asyncio
import typing
import os

import discord
from discord.ext import commands

import captcha as c
import settings as s
import play as p

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tokenBeta = os.getenv('DTB')
token = os.getenv('DT')

play_task = None


@bot.event
async def on_ready():
    print("Je suis prêt")

    for server in bot.guilds:
        print(f'{server.name}(id: {server.id})')
    print("Début de la synchronisation")

    for guild in bot.guilds:
        if settings[guild.name]["query"] is not None:
            settings[guild.name]["query"] = []

    await bot.tree.sync()

    print("Synchronisation terminée\n")

    commandes = bot.tree.get_commands()

    for command in commandes:
        print(f"Commande : {command.name}")
        print(f"Description : {command.description}")
        print("------------------------")


@bot.event
async def on_guild_join(guild: discord.Guild):
    await s.create_settings(guild)
    print("nouveau serveur ajouté à la configuration")


@bot.event
async def on_guild_remove(guild: discord.Guild):
    await s.delete_settings(guild)
    print(f"le serveur {guild.name} a été supprimé des de la config")


@bot.event
async def on_member_join(member):
    try:
        channel = member.guild.get_channel(settings[member.guild.name]["verificationChannel"])
        print(member.guild.get_role(settings[member.guild.name]["roleBefore"]))
        await member.add_roles(member.guild.get_role(settings[member.guild.name]["roleBefore"]))
        try:
            await channel.send(
                f"Bienvenue {member.mention} ! Veuillez utiliser la commande `/verify`")
        except discord.Forbidden:
            await channel.send(
                "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
    except AttributeError:
        await channel.send(":warning: Le bot ne trouve pas le rôle d'arrivée")


@bot.tree.command(name="setrole", description="Permet de configurer le rôle d'arrivée et celui après la vérification")
@discord.app_commands.describe(option="Before : rôle à l'arrivée, After : rôle après vérification",
                               role="Le rôle que vous voulez sélectionner")
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
@discord.app_commands.describe(channel="Le salon dans lequel vous voulez envoyer le message de bienvenue")
@commands.has_permissions(administrator=True)
async def setchannel(interaction, channel: discord.TextChannel):
    await s.set_verification_channel(interaction, channel)
    await s.save()


@bot.tree.command(name="settimeout", description="Permet de configurer le temps en seconde avant expiration du captcha")
@discord.app_commands.describe(time="Le temps en secondes avant expiration de `/verify`")
@commands.has_permissions(administrator=True)
async def settimeout(interaction, time: int):
    await s.set_timeout(interaction, time)
    await s.save()


@bot.tree.command(name="aide", description="affiche les informations sur les différentes commandes")
async def aide(interaction: discord.Interaction, commande: str = None):
    roleBefore = interaction.guild.get_role(settings[interaction.guild.name]["roleBefore"])
    roleAfter = interaction.guild.get_role(settings[interaction.guild.name]["roleAfter"])
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


@bot.tree.command(name="settings",
                  description="Affiche les différents paramètres mis en place (admin uniquement)")  # à améliorer
@commands.has_permissions(administrator=True)
async def settings(interaction):
    salon = interaction.guild.get_channel(settings[interaction.guild.name]["verificationChannel"])
    roleBefore = interaction.guild.get_role(settings[interaction.guild.name]["roleBefore"])
    roleAfter = interaction.guild.get_role(settings[interaction.guild.name]["roleAfter"])
    embed = discord.Embed(title="paramètre du bot :")
    embed.add_field(name="Salon de vérification : ", value=salon.mention)
    embed.add_field(name="Rôle d'arrivée : ", value=roleAfter.mention)
    embed.add_field(name="Rôle après vérification : ", value=roleBefore.mention)
    embed.add_field(name="Temps de la commande vérification : ", value=settings[interaction.guild.name]["timeout"])
    embed.add_field(name="Nombre d'essais : ", value=settings[interaction.guild.name]["nbEssais"])
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="verify", description="Permet de lancer la vérification")
async def verify(interaction: discord.Interaction):
    if not (interaction.guild.get_role(settings[interaction.guild.name]["roleBefore"]) in interaction.user.roles):
        await interaction.response.send_message(":warning: Vous avez déjà effectué la vérification")
    elif settings[interaction.guild.name]["verificationChannel"] == 0 or settings[interaction.guild.name][
        "roleBefore"] == 0 or settings[interaction.guild.name]["roleAfter"] == 0:
        await interaction.response.send_message(
            ":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation"
        )
    else:
        continuer = True
        tmps = settings[interaction.guild.name]["timeout"] / 60
        nb = settings[interaction.guild.name]["nbEssais"]
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
                reponse = await bot.wait_for('message', check=check,
                                             timeout=settings[interaction.guild.name]["timeout"])
            except TimeoutError:
                await interaction.channel.send("Temps écoulé ! Veuillez recommencer")

            # Agir en fonction de la réponse de l'utilisateur
            if reponse.content == code:
                await interaction.channel.send(f"Le code est bon ! Bienvenue sur {interaction.guild.name}")
                await interaction.user.add_roles(
                    interaction.guild.get_role(settings[interaction.guild.name]["roleAfter"]))
                await asyncio.sleep(0.5)
                await interaction.user.remove_roles(
                    interaction.guild.get_role(settings[interaction.guild.name]["roleBefore"]))
                continuer = False

                await interaction.channel.purge()
            else:
                await interaction.channel.send("Code incorrect... Veuillez recommencer.")
                await interaction.channel.purge()


@bot.tree.command(name="play", description="Lance un audio via l'URL youtube")
async def play(interaction: discord.Interaction, url: str):
    if interaction.guild.name not in settings["authorized"]:
        await interaction.response.send_message(":warning: Ce serveur n'est pas autorisé à utiliser cette commande")
    global play_task
    vc = None
    state = interaction.user.voice
    if state is None:
        await interaction.response.send_message("Vous devez être dans un salon vocal pour utiliser cette commande")
    else:

        if interaction.guild.voice_client is None:
            vc = await state.channel.connect()
            embed = await p.add_audio(interaction, url, 0, settings)
            await interaction.response.send_message(embed=embed)
        else:
            embed = await p.add_audio(interaction, url, 1, settings)
            await interaction.response.send_message(embed=embed)

        if play_task is None:
            play_task = asyncio.create_task(boucle_musique(interaction, vc))


async def boucle_musique(interaction, vc):
    global play_task
    first = True
    while vc.is_connected():
        global settings
        query = settings[interaction.guild.name]["query"]
        if not vc.is_playing():
            if len(query) > 0:
                if not first:
                    embed = p.create_embed(interaction, "Now playing : " + query[0].title, query[0].url, settings)
                    await interaction.channel.send(embed=embed)
                try :
                    p.play_audio(interaction, vc, settings)
                except discord.app_commands.errors.CommandInvokeError:
                    await interaction.channel.send(":warning: le bot ne peut actuellement pas lancer l'audio")
                    await vc.disconnect()
                while vc.is_playing():
                    await asyncio.sleep(1)
                await asyncio.sleep(1)
                query = p.supprimer_musique(interaction, query)
        first = False
        await asyncio.sleep(1)
    play_task = None


@bot.tree.command(name="skip", description="Passe à la musique suivante")
async def skip(interaction):
    if len(settings[interaction.guild.name]["query"]) < 1:
        await interaction.response.send_message(":warning: Il n'y a pas de musique après celle-ci")
    else:
        interaction.guild.voice_client.stop()
        embed = discord.Embed(title=":next_track: Skip")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stop", description="Stop la musique et déconnecte le bot")
async def stop(interaction: discord.Interaction):
    state = interaction.guild.voice_client
    if state is None:
        await interaction.response.send_message("Le bot est connecté à aucun salon vocal")
    else:
        await state.disconnect()
        p.supprimer_musique(interaction, settings[interaction.guild.name]["query"])
        settings[interaction.guild.name]["query"].clear()
        await interaction.response.send_message("Déconnecté")


@bot.tree.command(name="queue", description="Affiche la liste de lecture")
async def queue(interaction):
    embed = discord.Embed(title="Liste de lecture")
    query = settings[interaction.guild.name]["query"]
    if len(query) <=0 :
        await interaction.response.send_message(":warning: La liste est vide")
    else:
        for i in range(len(query)):
            embed.add_field(name=str(i+1) + ". " + query[i].title,value="", inline=False)
        await interaction.response.send_message(embed=embed)


def run():
    choix = int(input("Quelle mode voulez vous lancer ?\n 1. Normal (SpoonCAPTCHA)\n 2. Bêta (SogataBot)"))
    if choix == 1:
        bot.run(token)
    elif choix == 2:
        bot.run(tokenBeta)


if __name__ == "__main__":
    settings = s.loading()
    run()
