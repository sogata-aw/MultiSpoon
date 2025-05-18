import typing
import asyncio

import discord
from discord.ext import commands

from view.aideView import AideSelectView
from utilities import captchas as c, settings as s
from utilities import embeds as e


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----Commandes-----

    @commands.hybrid_command(name="set-role",
                             description="Permet de configurer le rôle d'arrivée et celui après la vérification")
    @discord.app_commands.describe(option="Arrivée : rôle à l'arrivée, vérifié : rôle après vérification",
                                   role="Le rôle que vous voulez sélectionner")
    @commands.has_permissions(administrator=True)
    async def set_role(self, ctx, option: str, role: discord.Role):
        if option == "arrivée":
            await s.set_role_before(ctx, role, self.bot.settings)
        elif option == "vérifié":
            await s.set_role_after(ctx, role, self.bot.settings)
        s.save(self.bot.settings)

    @commands.hybrid_command(name="set-channel",
                             description="Permet de configurer le salon ou sera envoyé le message quand quelqu'un arrive sur le serveur")
    @discord.app_commands.describe(channel="Le salon dans lequel vous voulez envoyer le message de bienvenue")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        await s.set_verification_channel(ctx, channel, self.bot.settings)
        s.save(self.bot.settings)

    @commands.hybrid_command(name="set-timeout",
                             description="Permet de configurer le temps en seconde avant expiration du captcha")
    @discord.app_commands.describe(time="Le temps en secondes avant expiration de `/verify`")
    @commands.has_permissions(administrator=True)
    async def set_timeout(self, ctx, time: int):
        await s.set_timeout(ctx, time, self.bot.settings)
        s.save(self.bot.settings)

    @commands.hybrid_command(name="aide", description="affiche les informations sur les différentes commandes")
    async def aide(self, ctx, commande: str = None):
        if commande is None:
            embed = discord.Embed(title="Choisissez une catégorie")
            await ctx.send(embed=embed, view=AideSelectView())

        elif commande == "music":
            await ctx.send(embed=await e.embed_aide(commande, self.bot.settings["commands"]["music"]),
                           view=AideSelectView())

        elif commande == "moderation":
            await ctx.send(embed=await e.embed_aide(commande, self.bot.settings["commands"]["music"]),
                           view=AideSelectView())

    @commands.hybrid_command(name="settings",
                             description="Affiche les différents paramètres mis en place (admin uniquement)")  # à améliorer
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):

        salon = ctx.guild.get_channel(self.bot.settings["guild"][ctx.guild.name]["verificationChannel"])
        role_before = ctx.guild.get_role(self.bot.settings["guild"][ctx.guild.name]["roleBefore"])
        role_after = ctx.guild.get_role(self.bot.settings["guild"][ctx.guild.name]["roleAfter"])

        embed = discord.Embed(title="paramètre du bot :")
        embed.add_field(name="Salon de vérification : ", value=salon.mention)
        embed.add_field(name="Rôle d'arrivée : ", value=role_before.mention)
        embed.add_field(name="Rôle après vérification : ", value=role_after.mention)
        embed.add_field(name="Temps de la commande vérification : ",
                        value=self.bot.settings["guild"][ctx.guild.name]["timeout"])
        embed.add_field(name="Nombre d'essais : ", value=self.bot.settings["guild"][ctx.guild.name]["nbEssais"])

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="verify", description="Permet de lancer la vérification")
    async def verify(self, ctx):
        reponse = None
        if not (ctx.guild.get_role(self.bot.settings["guild"][ctx.guild.name]["roleBefore"]) in ctx.author.roles):
            await ctx.send(":warning: Vous avez déjà effectué la vérification")

        elif ctx.author.name in self.bot.settings["guild"][ctx.guild.name]["inVerification"]:
            await ctx.channel.send(":warning: Vous êtes déjà en train de faire une vérification ! si vous avez raté le code donnée, attendez que le bot regénère un code")

        elif self.bot.settings["guild"][ctx.guild.name]["verificationChannel"] == 0 or \
                self.bot.settings["guild"][ctx.guild.name][
                    "roleBefore"] == 0 or self.bot.settings["guild"][ctx.guild.name]["roleAfter"] == 0:

            await ctx.send(
                ":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation"
            )
        else:
            self.bot.settings["guild"][ctx.guild.name]["inVerification"].append(ctx.author.name)
            continuer = True
            tmps = self.bot.settings["guild"][ctx.guild.name]["timeout"] / 60
            nb = self.bot.settings["guild"][ctx.guild.name]["nbEssais"]

            while continuer:
                code = c.generer_code()
                c.generer_image(code)
                attachement = discord.File("img/captcha.png", filename="img/captcha.png")

                await ctx.send(
                    f"{ctx.author.name} veuillez rentrer le code du captcha **en minuscule**, vous avez {int(tmps)} minutes pour le faire",
                    file=attachement)

                def verify_check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel

                def msg_check(msg):
                    return (msg.author == ctx.author
                            or (ctx.bot.user == msg.author
                                and (ctx.author.name.lower() in msg.content.lower()
                                                                or msg.content.lower() == f"Le code est bon ! Bienvenue sur {ctx.guild.name}".lower()
                                     or msg.content.lower() == "Code incorrect... Veuillez recommencer.".lower())))

                try:
                    reponse = await self.bot.wait_for('message', check=verify_check,
                                                      timeout=self.bot.settings["guild"][ctx.guild.name]["timeout"])

                    # Agir en fonction de la réponse de l'utilisateur
                    if reponse.content == code:
                        self.bot.settings["guild"][ctx.guild.name]["inVerification"].remove(ctx.author.name)

                        await ctx.channel.send(f"Le code est bon ! Bienvenue sur {ctx.guild.name}")
                        await ctx.author.add_roles(
                            ctx.guild.get_role(self.bot.settings["guild"][ctx.guild.name]["roleAfter"]))

                        await asyncio.sleep(0.5)

                        await ctx.author.remove_roles(
                            ctx.guild.get_role(self.bot.settings["guild"][ctx.guild.name]["roleBefore"]))
                        continuer = False

                        await ctx.channel.purge(limit=50, check=msg_check)

                    else:
                        await ctx.channel.send("Code incorrect... Veuillez recommencer.")
                        await asyncio.sleep(0.5)
                        await ctx.channel.purge(limit=50, check=msg_check)

                except asyncio.TimeoutError:
                    self.bot.settings["guild"][ctx.guild.name]["inVerification"].remove(ctx.author.name)


    # -----autocomplete-----

    # Setrole
    @set_role.autocomplete("option")
    async def autocomplete_option(self, ctx, option: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["arrivée", "vérifié"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste

    # Aide

    @aide.autocomplete("commande")
    async def autocomplete_commande(self, ctx, commande: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for cat in self.bot.settings["commands"]:
            liste.append(discord.app_commands.Choice(name=cat, value=cat))

        return liste


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
