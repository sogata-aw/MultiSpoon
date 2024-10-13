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


@bot.event
async def on_member_join(member):
    try:
        channel = member.guild.get_channel(settings["verificationChannel"])
        print(member.guild.get_role(settings["roleBefore"]))
        await member.add_roles(member.guild.get_role(settings["roleBefore"]))
        try:
            await channel.send(
                f"Bienvenue {member.mention} ! Veuillez utiliser la commande `!verify`")
        except discord.Forbidden:
            await channel.send(
                "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
    except AttributeError:
        await channel.send(":warning: Le bot ne trouve pas le rôle d'arrivée")


@bot.tree.command(name="set", description="Permet de configurer le bot")
@commands.has_permissions(administrator=True)
async def set(interaction, option: str, value: int):
    if option == "role_before":
        await s.set_role_before(interaction, value)
    elif option == "role_after":
        await s.set_role_after(interaction, value)
    elif option == "channel":
        await s.set_verification_channel(interaction, value)
    elif option == "time":
        await s.set_timeout(interaction, value)
    else:
        await interaction.response.send_message(":warning: La commande est invalide \n Veuillez lire la documentation avec la commande `!aide`")
    await s.save()

set.options = [
    {"name" : "option", "type" : 3, "description" : "Sélectionnez quelle paramètre modifier"},
    {"name" : "value", "type" : 4, "description" : "Rentrez un ID ou un temps en seconde en fonction de l'option choisie"}
]

@bot.tree.command(name="afficher", description="Affiche les différents paramètres mis en place (admin uniquement)")
@commands.has_permissions(administrator=True)
async def afficher(interaction):
    out = ""
    for key in settings:
        if not key == "token" :
            out += (f"{key} : {settings[key]}\n")
    await interaction.response.send_message(f"Voici les différents paramètres :\n{out}")


@bot.command()
async def verify(ctx):
    if not (ctx.guild.get_role(settings["roleBefore"]) in ctx.author.roles):
        await ctx.send(":warning: Vous avez déjà effectué la vérification")
    elif settings["verificationChannel"] == 0 or settings["roleBefore"] == 0 or settings["roleAfter"] == 0:
        await ctx.send(
            ":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation"
        )
    else:
        width, height = 400, 200
        taille = 6
        continuer = True
        tmps = settings["timeout"] / 60
        nb = settings["nbEssais"]
        while continuer:
            code = c.generer_code(taille)
            print(code)
            c.creer_captcha(code, width, height)
            attachement = discord.File("captcha.png", filename="captcha.png")
            await ctx.send(
                f"Veuillez rentrer le code du captcha, vous avez {tmps} minutes pour le faire et {nb} avant de devoir contacter un administrateur ",
                file=attachement)

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            try:
                reponse = await bot.wait_for('message', check=check, timeout=settings["timeout"])
            except TimeoutError:
                ctx.send("Temps écoulé ! Veuillez recommencer")

            # Agir en fonction de la réponse de l'utilisateur
            if reponse.content == code:
                await ctx.send(f"Le code est bon ! Bienvenue sur {ctx.guild.name}")
                await ctx.author.remove_roles(ctx.guild.get_role(settings["roleBefore"]))
                await ctx.author.add_roles(ctx.guild.get_role(settings["roleAfter"]))
                continuer = False
                await ctx.purge()
            else:
                await ctx.send("Code incorrect... Veuillez recommencer.")
                await ctx.purge()





settings = s.loading()
bot.run(settings["token"])
