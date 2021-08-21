import discord
from discord.ext import commands
import asyncio
import logging
import motor.motor_asyncio
import certifi
from discord_slash import SlashCommand 
import os

logging.basicConfig(
    level    = logging.INFO,
    format   = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt  = '%I:%M:%S %p')

bot = commands.Bot(command_prefix = '/', case_insensitive=True, intents = discord.Intents.all())
slash = SlashCommand(bot,sync_commands=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    """ When the bot opens the websocket connection """
    print("Connected to " + bot.user.name)
    await bot.wait_until_ready()
    bot.Tricked_guild_instance = bot.get_guild(759418498228158465)
    bot.twitch_role_log_channel = bot.get_channel(876463380020469810)
    bot.twitch_mod_id = 874310509732720700
    bot.twitch_embed_colour = discord.Color.dark_purple()
    bot.getTwitchEmbed = bot.get_cog('TrickTwitchCustomRolesEmbeds')
    bot.getTwitchComponent = bot.get_cog('TrickTwitchCustomRolesComponents')
    bot.getTwitchCommandUtil = bot.get_cog('TrickTwitchCustomRolesCommandUtil')
    bot.getTwitchRoleUtil = bot.get_cog('TrickTwitchCustomRolesUtil')
    bot.Ongoing_TrickTwitch_CustomRoles = {}
    bot.TrickTwitch_CustomRoles_RedeemedUserList = []
    bot.bannedRoleWords = []
    
MongoDB = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL,tlsCAFile=certifi.where()) #To stop the [SSL: CERTIFICATE_VERIFY_FAILED] ERRORS
db=MongoDB["Tricked-Bot"]
bot.db=db

for filename in os.listdir('./TrickTwitchRoles'):
    if filename.endswith('.py'):
        bot.load_extension(f'TrickTwitchRoles.{filename[:-3]}')

async def load_twitch_roles_roles():
    """ Loads up all role data"""
    bot.TrickTwitch_CustomRoles_Dict = {}
    cursor = bot.db["trick-twitch"].find( {} )
    async for document in cursor:
        discordID = document["discord_id"]
        roleList = document["roles"]
        bot.TrickTwitch_CustomRoles_Dict[discordID] = roleList
    await cursor.close()

loop = asyncio.get_event_loop()
bot.loop.run_until_complete(load_twitch_roles_roles())

bot.run(BOT_TOKEN)
