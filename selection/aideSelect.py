from typing import Any

import discord

from utilities import embeds as e

class AideSelect(discord.ui.Select):
    def __init__(self):
        options =[
            discord.SelectOption(label="Modération",emoji="🛠️"),
            discord.SelectOption(label="Musique", emoji="🎵")
        ]
        super().__init__(placeholder="Choisissez une option", max_values=1, min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction) -> Any:
        embed = None
        if self.values[0] == "Modération":
            dico = {"settings" : "Affiche les différents paramètres mis en place (admin uniquement)",
                    "setrole" : "Permet de configurer le rôle d'arrivée et celui après la vérification",
                    "setchannel" : "Permet de configurer le salon ou sera envoyé le message quand quelqu'un arrive sur le serveur",
                    "settimeout" : "Permet de configurer le temps en seconde avant expiration du captcha",
                    "verify" : "Permet de lancer la vérification"}
            embed = await e.embed_aide(self.values[0], dico)
        elif self.values[0] == "Musique":
            dico = {"play" : "Lance un audio via l'URL youtube",
                    "skip" : "Passe à la musique suivante",
                    "stop" : "Stop la musique et déconnecte le bot",
                    "queue" : "Affiche la liste de lecture",
                    "request" : "Envoie une demande au modérateur du bot pour pouvoir activer les commandes musicales"}
            embed = await e.embed_aide(self.values[0], dico)
        await interaction.response.edit_message(embed=embed)

class AideSelectView(discord.ui.View):
    def __init__(self, * ,timeout = 180):
        super().__init__(timeout= timeout)
        self.add_item(AideSelect())

