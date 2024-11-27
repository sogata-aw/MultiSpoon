import discord
import json


async def set_timeout(ctx, sec, settings):
    if sec < 30:
        await ctx.send(":warning: Le temps est invalide ! Il doit être supérieur à 30 secondes")
    else:
        settings[ctx.guild.name]["timeout"] = sec
        await ctx.send("✅ Le temps avant expiration du captcha a été mis à jour")


async def set_role_before(ctx, role, settings):
    if role is None or not isinstance(role, discord.Role):
        await ctx.send(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings[ctx.guild.name]["roleBefore"] = role.id
        await ctx.send("✅ Le rôle d'arrivée a été mis à jour")


async def set_role_after(ctx, role, settings):
    if role is None or not isinstance(role, discord.Role):
        await ctx.send(":warning: Le rôle sélectionné n'est pas valide")
    else:
        settings[ctx.guild.name]["roleAfter"] = role.id
        await ctx.send("✅ Le rôle après vérification a été mis à jour")


async def set_verification_channel(ctx, channel, settings):
    if channel is None or not isinstance(channel, discord.TextChannel):
        await ctx.send(":warning: Le salon selectionné n'est pas valide")
    else:
        settings[ctx.guild.name]["verificationChannel"] = channel.id
        await ctx.send("✅ Le salon des vérifications a été mis à jour")


async def create_settings(guild, settings):
    settings[guild.name] = {"verificationChannel": 0,
                            "roleBefore": 0,
                            "roleAfter": 0,
                            "timeout": 300,
                            "nbEssais": 3,
                            "tempChannels" : [],
                            "tempRoles" : [],
                            "logchannel": 0
                            }
    save(settings)


async def delete_settings(guild, settings):
    del settings[guild.name]
    save(settings)


def save(settings):
    with open("./settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def loading():
    with open("./settings.json", "r", encoding="utf-8") as file:
        return json.load(file)
