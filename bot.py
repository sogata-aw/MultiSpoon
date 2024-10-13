import discord
from discord.ext import commands
import captcha as c
import json

token = "MTIzMDg3MTE4Mzk0ODI1MTIwNg.GHuaO0._tOPpvXSzG3QHB-q01fax0yVdDpd6fYPiQGxfY"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Je suis prêt")
    for server in bot.guilds:
        print(f'{server.name}(id: {server.id})')


@bot.event
async def on_member_join(member):
    try :
        channel = member.guild.get_channel(settings["verificationChannel"])
        print(member.guild.get_role(settings["roleBefore"]))
        await member.add_roles(member.guild.get_role(settings["roleBefore"]))
        try:
            await channel.send(
                f"Bienvenue {member.mention} ! Veuillez utiliser la commande `!verify`")
        except discord.Forbidden:
            await channel.send(
                "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
    except AttributeError :
        await channel.send(":warning: Le bot ne trouve pas le rôle d'arrivée")


@bot.command()
@commands.has_permissions(administrator=True)
async def set(ctx, option: str, value: int):
    if option == "role_before":
        await set_role_before(ctx, value)
    elif option == "role_after":
        await set_role_after(ctx, value)
    elif option == "channel":
        await set_verification_channel(ctx, value)
    elif option == "time":
        await set_timeout(ctx, value)
    else:
        await ctx.send(":warning: La commande est invalide \n Veuillez lire la documentation avec la commande `!aide`")
    await save()


@bot.command()
@commands.has_permissions(administrator=True)
async def afficher(ctx):
    await ctx.send("Voici les différents paramètres")
    for key,value in settings.items():
        await ctx.send(f"{key} : {value}")

@bot.command()
async def verify(ctx):
    if not (ctx.guild.get_role(settings["roleBefore"]) in ctx.author.roles)  :
        await ctx.send(":warning: !!! Vous avez déjà effectué la vérification")
    elif settings["verificationChannel"] == 0 or settings["roleBefore"] == 0 or settings["roleAfter"] == 0:
        await ctx.send(":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation")
    else:
        width, height = 400, 200
        taille = 6
        continuer = True
        while continuer:
            code = c.generer_code(taille)
            print(code)
            c.creer_captcha(code, width, height)
            attachement = discord.File("captcha.png", filename="captcha.png")
            await ctx.send("Veuillez rentrer le code du captcha, vous avez 5 minutes pour le faire", file=attachement)

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
            else:
                await ctx.send("Code incorrect... Veuillez recommencer.")


async def set_timeout(ctx, sec):
    if sec < 30:
        await ctx.send(":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes")
    else:
        settings["timeout"] = sec


async def set_role_before(ctx, id):
    role = ctx.guild.get_role(id)
    if role is None or not isinstance(role, discord.Role):
        await ctx.send(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings["roleBefore"] = id
        await ctx.send("✅ Le rôle d'arrivée a été mis à jour")


async def set_role_after(ctx, id):
    role = ctx.guild.get_role(id)
    if role is None or not isinstance(role, discord.Role):
        await ctx.send(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings["roleAfter"] = id
        await ctx.send("✅ Le rôle après vérification a été mis à jour")


async def set_verification_channel(ctx, id):
    salon = ctx.guild.get_channel(id)
    if salon is None or not isinstance(salon, discord.TextChannel):
        await ctx.send(":warning: Le salon selectionné n'est pas valide")
    else:
        settings["verificationChannel"] = id
        await ctx.send("✅ Le salon des vérifications a été mis à jour")


async def save():
    with open("settings.json", "w") as file:
        json.dump(settings, file)


def loading():
    with open("settings.json", "r") as file:
        return json.load(file)


settings = loading()
bot.run("MTIzMDg3MTE4Mzk0ODI1MTIwNg.GHuaO0._tOPpvXSzG3QHB-q01fax0yVdDpd6fYPiQGxfY")
