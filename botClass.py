import discord
from discord.ext import commands
import captcha as c
import settings
import os

tokenBeta = os.getenv('DTB')

class SpoonCAPTCHA(commands.Bot):
    def __init__(self,intents,token):
        super().__init__(command_prefix="!", intents=intents)
        self.token = token


    async def on_ready(self):
        print("Je suis prêt")
        for server in self.guilds:
            print(f'{server.name}(id: {server.id})')
        print("Début de la synchronisation")
        await bot.tree.sync()
        print("Synchronisation terminée")
        commandes = bot.tree.get_commands()
        for command in commandes:
            print(f"Commande : {command.name}")
            print(f"Description : {command.description}")
            print("------------------------")

    async def on_member_join(self,member):
        channel = member.guild.get_channel(1272201109259157568)
        role = member.guild.get_role(1294342786874871869)
        try:
            await member.add_roles(role)
            await channel.send(f"Bienvenue {member.mention}")
        except discord.Forbidden:
            await channel.send(
                "Le bot n'a pas les permissions nécessaires ! Essayez de mettre son rôle au-dessus des autres")
    @commands.command(name="verify")
    async def verify(self,ctx):
        width, height = 400, 200
        taille = 6
        continuer = True
        while continuer:
            code = c.generer_code(taille)
            c.creer_captcha(code, width, height)
            attachement = discord.File("captcha.png", filename="captcha.png")
            await ctx.send("Veuillez rentrer le code du captcha, vous avez 5 minutes pour le faire", file=attachement)

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            try:
                reponse = await self.wait_for('message', check=check, timeout=300)
            except TimeoutError:
                ctx.send("Temps écoulé")

            # Agir en fonction de la réponse de l'utilisateur
            await ctx.send(code)
            if reponse.content == code:
                await ctx.send(f"Le code est bon ! Bienvenue sur {ctx.guild.name}")
                continuer = False
            else:
                await ctx.send("Code incorrect... Veuillez recommencer.")

    def run(self):
        super().run(self.token)

if __name__ == "__main__":
    settings = settings.loading()
    bot = SpoonCAPTCHA(discord.Intents.all(),tokenBeta)
    bot.run()