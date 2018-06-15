import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import datetime
import pickle

VERSION = "0.1"

manage_roles = {}   # List of role id's that are allowed to manage the bot
token = ""          # Your bot token goes here
prefix = "%"        # Your preferred command prefix

Client = discord.Client()
bot = commands.Bot(command_prefix=prefix)
allowed_channels = {"440720123448393728"}
timeout = datetime.datetime()
user_timeouts = dict()
user_score = dict()


# Verifies if the role list of the user has a role that is allowed to manage the bot
def can_manage(roles):
    for role in roles:
        for manage_role in manage_roles:
            if role == manage_role:
                return True
    return False


# 3 simple methods for the sake of code clarity
def on_timeout():
    return datetime.datetime.now() < timeout


def user_on_timeout(user_id):
    if user_id in user_timeouts:
        return datetime.datetime.now() < user_timeouts[user_id]
    return False


# The bot stores data between sessions in a data.data file in the scripts repository
def save():
    file = open("data.data", "w")
    pickle.dump([allowed_channels, timeout, user_timeouts, user_score], file)


@bot.event
async def on_ready():
    global allowed_channels, timeout, user_timeouts, user_score
    try:
        file = open("data.data", "r")
        allowed_channels, timeout, user_timeouts, user_score = pickle.load(file)
    except IOError:
        print("No data file appears to exist, initializing variables")
        allowed_channels = []
        timeout = datetime.datetime.now()
        user_timeouts = dict()
        user_timeouts = dict()
print("Bot is ready!")


# Management commands
@bot.command(name="allow")
async def bot_allow(message):
    if message.author == bot:
        return
    cont = str(message.content)
    if message.author.id in manage_roles:
        args = cont.split(sep=" ")
        try:
            x = args[1]
        except IndexError:
            x = message.channel.id
        allowed_channels.add(x)
        await bot.say("Added channel <#%s> to the allowed list" % x)
    else:
        await bot.say("You do not have the permission to use that command")


@bot.command(name="shutdown")
async def bot_shutdown(message):
    if message.author == bot:
        return
    if message.author.id in manage_roles:
        await bot.say("Shutting down...")
        await bot.logout()
    else:
        await bot.say("You do not have the permission to use that command")


# All user commands
@bot.command(name="info")
async def bot_info(message):
    if message.author == bot:
        return
    await bot.say("DankBot %s (https://github.com/oscaretti/DankBot)" % VERSION)

bot.run(token)
