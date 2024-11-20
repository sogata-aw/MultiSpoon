import typing
import asyncio

import discord
from discord.ext import commands

from selection import aideSelect as a
from utilities import captcha as c, settings as s


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="setrole",
                             description="Permet de configurer le rôle d'arrivée et celui après la vérification")
    @discord.app_commands.describe(option="Arrivée : rôle à l'arrivée, vérifié : rôle après vérification",
                                   role="Le rôle que vous voulez sélectionner")
    @commands.has_permissions(administrator=True)
    async def setrole(self, ctx, option: str, role: discord.Role):
        if option == "arrivée":
            await s.set_role_before(ctx, role, self.bot.settings)
        elif option == "vérifié":
            await s.set_role_after(ctx, role, self.bot.settings)
        s.save(self.bot.settings)

    @setrole.autocomplete("option")
    async def autocomplete_option(self, ctx, option: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["arrivée", "vérifié"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste

    @commands.hybrid_command(name="setchannel",
                             description="Permet de configurer le salon ou sera envoyé le message quand quelqu'un arrive sur le serveur")
    @discord.app_commands.describe(channel="Le salon dans lequel vous voulez envoyer le message de bienvenue")
    @commands.has_permissions(administrator=True)
    async def setchannel(self, ctx, channel: discord.TextChannel):
        await s.set_verification_channel(ctx, channel, self.bot.settings)
        s.save(self.bot.settings)

    @commands.hybrid_command(name="settimeout",
                             description="Permet de configurer le temps en seconde avant expiration du captcha")
    @discord.app_commands.describe(time="Le temps en secondes avant expiration de `/verify`")
    @commands.has_permissions(administrator=True)
    async def settimeout(self, ctx, time: int):
        await s.set_timeout(ctx, time, self.bot.settings)
        s.save(self.bot.settings)

    @commands.hybrid_command(name="aide", description="affiche les informations sur les différentes commandes")
    async def aide(self, ctx, commande: str = None):
        if commande is None:
            embed = discord.Embed(title="Choisissez une catégorie")
            await ctx.send(embed=embed, view=a.AideSelectView())


    @commands.hybrid_command(name="settings",
                             description="Affiche les différents paramètres mis en place (admin uniquement)")  # à améliorer
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        salon = ctx.guild.get_channel(self.bot.settings[ctx.guild.name]["verificationChannel"])
        rolebefore = ctx.guild.get_role(self.bot.settings[ctx.guild.name]["rolebefore"])
        roleafter = ctx.guild.get_role(self.bot.settings[ctx.guild.name]["roleafter"])
        embed = discord.Embed(title="paramètre du bot :")
        embed.add_field(name="Salon de vérification : ", value=salon.mention)
        embed.add_field(name="Rôle d'arrivée : ", value=rolebefore.mention)
        embed.add_field(name="Rôle après vérification : ", value=roleafter.mention)
        embed.add_field(name="Temps de la commande vérification : ", value=self.bot.settings[ctx.guild.name]["timeout"])
        embed.add_field(name="Nombre d'essais : ", value=self.bot.settings[ctx.guild.name]["nbEssais"])
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="verify", description="Permet de lancer la vérification")
    async def verify(self, ctx):
        reponse = None
        if not (ctx.guild.get_role(self.bot.settings[ctx.guild.name]["roleBefore"]) in ctx.author.roles):
            await ctx.send(":warning: Vous avez déjà effectué la vérification")
        elif self.bot.settings[ctx.guild.name]["verificationChannel"] == 0 or self.bot.settings[ctx.guild.name][
            "roleBefore"] == 0 or self.bot.settings[ctx.guild.name]["roleAfter"] == 0:
            print(self.bot.settings)
            await ctx.send(
                ":warning: La configuration n'est pas complète \n Veuillez la finaliser avant de procéder à une vérifcation"
            )
        else:
            continuer = True
            tmps = self.bot.settings[ctx.guild.name]["timeout"] / 60
            nb = self.bot.settings[ctx.guild.name]["nbEssais"]
            while continuer:
                code = c.generer_code()
                print(code)
                c.creer_captcha(code)
                attachement = discord.File("img/captcha.png", filename="img/captcha.png")
                await ctx.send(
                    f"Veuillez rentrer le code du captcha, vous avez {int(tmps)} minutes pour le faire et {nb} avant de devoir contacter un administrateur ",
                    file=attachement)

                def check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel

                try:
                    reponse = await self.bot.wait_for('message', check=check,
                                                      timeout=self.bot.settings[ctx.guild.name]["timeout"])
                except TimeoutError:
                    await ctx.channel.send("Temps écoulé ! Veuillez recommencer")

                # Agir en fonction de la réponse de l'utilisateur
                if reponse.content == code:
                    await ctx.channel.send(f"Le code est bon ! Bienvenue sur {ctx.guild.name}")
                    await ctx.author.add_roles(
                        ctx.guild.get_role(self.bot.settings[ctx.guild.name]["roleAfter"]))
                    await asyncio.sleep(0.5)
                    await ctx.author.remove_roles(
                        ctx.guild.get_role(self.bot.settings[ctx.guild.name]["roleBefore"]))
                    continuer = False

                    await ctx.channel.purge()
                else:
                    await ctx.channel.send("Code incorrect... Veuillez recommencer.")
                    await ctx.channel.purge()

    @commands.hybrid_command(name="salontemporaire", description="Créer un salon pour une durée déterminée")
    @commands.has_permissions(administrator=True)
    async def salontemporaire(self, ctx, nom: str, typesalon: str, categorie: str = None):
        if typesalon == "textuel":
            for category in ctx.guild.categories:
                if category.name == categorie:
                    salon = await ctx.guild.create_text_channel(name=nom, reason=f"Salon temporaire qui expire dans ...",category=category)
                    await ctx.send(f"Salon crée ! {salon.mention}")
        elif typesalon == "vocal":
            for category in ctx.guild.categories:
                if category.name == categorie:
                    salon = await ctx.guild.create_text_channel(name=nom,
                                                                reason=f"Salon temporaire qui expire dans ...",
                                                                category=category)
                    await ctx.send(f"Salon crée ! {salon.mention}")
        else:
            await ctx.send(":warning: Le type de salon est invalide")

    @salontemporaire.autocomplete("typesalon")
    async def autocomplete_type(self, ctx, typesalon: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for choice in ["textuel", "vocal"]:
            liste.append(discord.app_commands.Choice(name=choice, value=choice))
        return liste

    @salontemporaire.autocomplete("categorie")
    async def autocomplete_category(self, ctx, categorie: str) -> typing.List[
        discord.app_commands.Choice[str]]:
        liste = []
        for category in ctx.guild.categories:
            liste.append(discord.app_commands.Choice(name=category.name, value=category.name))
        return liste


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
