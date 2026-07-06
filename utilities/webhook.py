import discord


async def get_webhook(channel: discord.TextChannel, name: str):
    webhooks = await channel.webhooks()
    webhook = next((w for w in webhooks if w.name == name), None)
    if not webhook:
        webhook = await channel.create_webhook(name=name)
    return webhook
