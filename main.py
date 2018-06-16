import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import datetime
import pickle
import random
import datetime_formatting

VERSION = "0.1"

manage_roles = {}   # List of role id's that are allowed to manage the bot
token = ""          # Your bot token goes here
prefix = ""         # Your preferred command prefix

Client = discord.Client()
bot = commands.Bot(command_prefix=prefix)
allowed_channels = {"440720123448393728"}


#   TODO
#   Add bodies to set_bot_cooldown() and set_user_cooldown()
#   Allow toggle on bot_allow()
#   Implement time display formatting
#   Replace redundant context.message.content.* with more readable alternatives


# Verifies if the role list of the user has a role that is allowed to manage the bot
def can_manage(roles):
    for role in roles:
        for manage_role in manage_roles:
            if role.id == manage_role:
                return True
    return False


# 3 simple methods for the sake of code clarity
def on_timeout():
    return datetime.datetime.now() < bot_timeout


def user_on_timeout(user_id):
    if user_id in user_timeouts:
        return datetime.datetime.now() < user_timeouts[user_id]
    return False


# The bot stores data between sessions in a data.data file in the scripts repository
def save():
    file = open("data.data", "wb")
    pickle.dump([allowed_channels, bot_timeout, user_timeouts, user_score,
                 user_cooldown, bot_cooldown, bot_cooldown_deviation], file)


@bot.event
async def on_ready():
    global allowed_channels, bot_timeout, user_timeouts, user_score, user_cooldown, bot_cooldown, bot_cooldown_deviation
    try:
        file = open("data.data", "rb")
        allowed_channels, bot_timeout, user_timeouts, user_score, \
            user_cooldown, bot_cooldown, bot_cooldown_deviation = pickle.load(file)
    except Exception:
        print("No data file appears to exist, initializing variables")
        allowed_channels = set()
        bot_timeout = datetime.datetime.now()
        user_timeouts = dict()
        user_score = dict()
        user_cooldown = datetime.timedelta(minutes=1)
        bot_cooldown = datetime.timedelta(minutes=10)
        bot_cooldown_deviation = 0.15
    print("Bot is ready!")


# Management commands
@bot.command(name="allow", pass_context=True)
async def bot_allow(context):
    cont = str(context.message.content)
    if can_manage(context.message.author.roles):
        args = cont.split(sep=" ")
        try:
            x = args[1]
        except IndexError:
            x = context.message.channel.id
        allowed_channels.add(x)
        save()
        await bot.say("Added channel <#%s> to the allowed list" % x)
    else:
        await bot.say("You do not have the permission to use that command")


@bot.command(name="shutdown", pass_context=True)
async def bot_shutdown(context):
    if can_manage(context.message.author.roles):
        save()
        await bot.say("Shutting down...")
        await bot.logout()
    else:
        await bot.say("You do not have the permission to use that command")


@bot.command(name="bot cooldown", pass_context=True)
async def set_bot_cooldown(context):
    return


@bot.command(name="user cooldown", pass_context=True)
async def set_user_cooldown(context):
    return


# All user commands
@bot.command(name="info")
async def bot_info():
    await bot.say("DankBot %s (https://github.com/oscaretti/DankBot)" % VERSION)


@bot.command(name="dank", pass_context=True)
async def bot_dank(context):
    if context.message.channel.id not in allowed_channels:
        return
    user = context.message.author.id
    if user_on_timeout(user):
        wait_time = user_timeouts[user] - datetime.datetime.now()
        await bot.say("Not so fast <@%s>, you have to wait %s to try again" %
                      (user, wait_time - datetime.timedelta(microseconds=wait_time.microseconds)))
    elif on_timeout():
        new_user_timeout = datetime.datetime.now() + user_cooldown
        await bot.say("Someone has just said that <@%s>! Try again in %s" % (user, user_cooldown))
        user_timeouts[user] = new_user_timeout
    else:
        if user in user_score:
            user_score[user] += 1
        else:
            user_score[user] = 1
        # Setting new timeout date
        now = datetime.datetime.now()
        bottom_range = now + (bot_cooldown - bot_cooldown_deviation * bot_cooldown)
        top_range = now + (bot_cooldown + bot_cooldown_deviation * bot_cooldown)
        random.seed()
        span = top_range - bottom_range
        span *= random.random()
        global bot_timeout
        bot_timeout = bottom_range + span
        save()
        await bot.say("It is pretty dank my dude. You have %i points so far <@%s>" % (user_score[user], user))


@bot.command(name="score", pass_context=True)
async def bot_score(context):
    if context.message.channel.id not in allowed_channels:
        return
    user = context.message.author.id
    if user in user_score:
        await bot.say("Your score is %i <@%s>" % (user_score[user], user))
    else:
        await bot.say("You don't have any score yet <@%s>" % user)


bot.run(token)
