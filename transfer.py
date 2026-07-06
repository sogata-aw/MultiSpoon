import sqlite3
import bdd

with open('Spoon.sql', 'r') as sql_file:
    sql_script = sql_file.read()

data = bdd.load_guilds()

db = sqlite3.connect('spoon.db')
cursor = db.cursor()
cursor.executescript(sql_script)
db.commit()

for key, guild in data.items():
    cursor = db.cursor()
    cursor.execute("""
               INSERT INTO Guild
               VALUES (:id, :name, :verification_channel, :role_before, :role_after, :timeout, :log_channel,
                       :white_list_active, :on_create_channel, :spoon_pot)""",
               {
                   "id": key,
                   "name": guild.name,
                   "verification_channel": guild.verificationChannel,
                   "role_before": guild.roleBefore,
                   "role_after": guild.roleAfter,
                   "timeout": guild.timeout,
                   "log_channel": guild.logChannel,
                   "white_list_active": guild.whiteListActive,
                   "on_create_channel": guild.onCreateChannel,
                   "spoon_pot": guild.spoonPot
               })
    db.commit()

    for user in guild.alreadyVerified:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO Verified VALUES(:user, :guild)""", {
            "user": user,
            "guild": key
        })
        db.commit()

    for channel in guild.channelToCheck:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO Trigger_Voice_Channel VALUES(:channel, :guild)""", {
            "channel": channel,
            "guild": key
        })
        db.commit()

    for channel in guild.tempChannels:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO Temp_Channel VALUES(:id, :guild, :name, :category, :type, :duree)""", {
            "id": channel.id,
            "guild": key,
            "name": channel.name,
            "category": channel.categorie,
            "type": channel.type,
            "duree": channel.duree,
        })
        db.commit()

    for channel in guild.tempVoiceChannels:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO Triggered_Voice_Channel VALUES(:channel, :guild)""", {
            "channel": channel,
            "guild": key
        })
        db.commit()

    for role in guild.tempRoles:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO Role VALUES(:id, :guild, :name, :duree)""", {
            "id": role.id,
            "guild": key,
            "name": role.name,
            "duree": role.duree,
        })
        db.commit()

    for channel in guild.whiteList:
        cursor = db.cursor()
        cursor.execute("""INSERT INTO White_List VALUES(:channel, :guild)""", {
            "channel": channel,
            "guild": key
        })

    for k, v in guild.associatedWith.items():
        for item in v:
            cursor = db.cursor()
            cursor.execute("""
                           INSERT INTO Link (channel_id, guild_id, linked_channel_id, linked_guild_id)
                           VALUES (:channel, :guild, :linked_channel, :linked_guild)
                           """, {
                               "channel": k,
                               "guild": key,
                               "linked_channel": item.channel,
                               "linked_guild": item.guild
                           })
            db.commit()

db.close()
