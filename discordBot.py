import json
import os
import random
from itertools import cycle

import discord
from discord.ext import commands, tasks


def get_prefix(client, message):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    
    return prefixes[str(message.guild.id)]

TOKEN = "Token here"
client = commands.Bot(command_prefix = get_prefix)

@client.event
async def on_ready():
    change_status.start()
    print("[ONLINE] Bot is now running")

#* Load prefixes.
@client.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes[str(guild.id)] = "!"
    
    with open("prefixes.json", "w"):
        json.dump(prefixes, f, ident = 4)

@client.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes.pop(str(guild.id))
    
    with open("prefixes.json", "w"):
        json.dump(prefixes, f, ident = 4)

@client.command()
async def changeprefix(ctx, prefix):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)
    
    prefixes[str(ctx.guild.id)] = prefix
    
    with open("prefixes.json", "w"):
        json.dump(prefixes, f, ident = 4)

#* Normal stuffs here.
@client.event
async def on_member_join(member):
    print(f"[JOIN] {member} has joined.")

@client.event
async def on_member_remove(member):
    print(f"[LEFT] {member} has left.")

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)} ms.")

@client.command()
@commands.has_permissions(manage_messages = True)
async def clear(ctx, amount = 0):
    if amount <= 0:
        ctx.send("Please specify the message amount. (Has to be bigger than one.)")
        return
    try:
        if amount < 50:
            await ctx.channel.purge(limit = amount)
        else:
            await ctx.send("Amount to delete should not exceed 50 messages.")
    except ValueError:
        ctx.send("Error.")

@client.command()
async def ban(ctx, member: discord.Member, *, reason = None):
    try:
        await member.ban(reason = reason)
        await ctx.send(f"Banned {member}.")
    except discord.errors.Forbidden:
        ctx.send("Error 403.")

@client.command()
async def unban(ctx, *, member):
    bans = await ctx.guild.bans()
    memberName, memberDiscriminator = member.split("#")
    for banEntry in bans:
        user = banEntry.user
        if (user.name, user.discriminator) == (memberName, memberDiscriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {member}.")

#! Handles some errors
#TODO Handle more error types.
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("[ERROR] Incorrect arguments.")
    elif isinstance(error, discord.errors.Forbidden):
        await ctx.send("[ERROR] Bot does not have perms for this command to execute.")

status = cycle(["Help I was trapped inside this bot please save me!", "01101001010010101010 - Error detected. Deleting intruder."])
@tasks.loop(seconds = 7)
async def change_status():
    await client.change_presence(activity = discord.Streaming(name = next(status), url = "https://www.twitch.tv/rainbow6"))

#* Logging the bot in.
client.run(TOKEN)
