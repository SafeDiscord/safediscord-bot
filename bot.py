# sources to read and learn about slash commands and  discord.py in general

# https://pypi.org/project/discord-py-slash-command/
# https://discordpy.readthedocs.io/en/rewrite/index.html
# https://realpython.com/how-to-make-a-discord-bot-python/

import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

#################################
# get tokens
#################################

from  dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


#################################
# get list of malicious accs
#################################

# import git

# SD_repo = git.Repo('https://github.com/SafeDiscord/safediscord-repo.git')
# SD_repo.remotes.origin.pull()
# read YAML into var


#################################
# set up client
#################################

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():

  print('Connecting to:')
  for guild in bot.guilds:
    print(' - ', guild.id, guild.name)
    # get config file for the guild, use source or something, load file up as variables

# @bot.event
# async def on_member_join(member):
  #check if UUID matches any from the YAML



#################################
# util funcs, start with _
#################################

# does user have perms

# is UUID bad


#################################
# set up commands
#################################

@slash.slash(
    name="check", 
    description="Check if a user is in the reports database",
    options=[
        create_option(
            name="username",
            description="Username to check",
            option_type=3,
            required=True
        )
    ])
async def _check(ctx, username):
    embed = discord.Embed(title="embed test")
    await ctx.send(content=username, embeds=[embed])


bot.run(TOKEN)



#################################
### settings for later date
#################################

# send_in_channel bool    - send warning messages in a specific channel
# warning_channel string  - channel ID (not name) to send warning messages within 
# role_required_for_cmd   - plaintext of lowest role required to run commands
