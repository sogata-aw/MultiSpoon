import os

import click
import discord
from dotenv import load_dotenv

from bot import MultiSpoon


@click.command()
@click.option("--no-dev", is_flag=True)
@click.option("--updated", is_flag=True)
def main(no_dev: bool, updated: bool):
    load_dotenv(".env")

    token = os.getenv("DT" if no_dev else "DTB")

    if not token:
        click.echo("No token found", err=True)
        return

    bot = MultiSpoon(discord.Intents.all(), updated)

    bot.run(token)


if __name__ == "__main__":
    main()
