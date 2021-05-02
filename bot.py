# sources to read and learn about slash commands and  discord.py in general

# https://pypi.org/project/discord-py-slash-command/
# https://discordpy.readthedocs.io/en/rewrite/index.html
# https://realpython.com/how-to-make-a-discord-bot-python/

import os
import yaml
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
# get yamls
#################################


# read reports YAML into var
def get_reports():
  with open('../safediscord-repo/reports.yaml') as reports_file:
    return yaml.load(reports_file, yaml.SafeLoader)

reports = get_reports()

# read guilds YAML into var
def get_guilds():
  with open('./guilds.yaml') as guilds_file:
    return yaml.load(guilds_file, yaml.SafeLoader)

saved_guilds = get_guilds()

def save_guilds(guilds):
  with open(r'./guilds.yaml', 'w') as guilds_file:
    return yaml.dump(guilds, guilds_file)

# read default guild settings YAML into var
def get_guild_defaults():
  with open('./new_guild_defaults.yaml') as new_guild_file:
    return yaml.load(new_guild_file, yaml.SafeLoader)

new_guild_defaults = get_guild_defaults()


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

    # check if guild is a new one
    if not guild.id in saved_guilds:
      print('new guild! adding to config, hold tight.')

      saved_guilds[guild.id] = new_guild_defaults
      save_guilds(saved_guilds)

    for member in guild.members:
      if member.bot: 
        return
      
      if not reports[member.id]:
        return
      
      report_count = reports[member.id]['report_count']
      s = "s" if report_count > 1 else ""
      print(f"found {report_count} report{s} for {member.name}#{member.discriminator}")

@bot.event
async def on_member_join(member):
  #check if UUID matches any from the YAML
  pass    


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

### general channel and role settings
  # send_in_channel           - bool      - send warning messages in a specific channel
  # warning_channel_id        - int       - channel to send warning messages within 
  # role_required_for_cmd     - role      - lowest role required to run commands

#### threshold groups: problematic, malicious, destructive (settings are repeated per level)
  # problematic 
    # warn_account_age      - int       - if account is newer than X days, run warn(). -1 to disable
    # warn_report_count     - int       - if account has X or more reports, run warn(). -1 to disable
    # warn_match_keywords   - list:str  - if any reports contain any of these words, run warn(). empty list to disable
    # warn_if_all_match     - bool      - only run warn() if all criteria match. if False, run if any criteria match

  # malicious
    # mali_account_age      - int       - if account is newer than X days, run mali(). -1 to disable
    # mali_report_count     - int       - if account has X or more reports, run mali(). -1 to disable
    # mali_match_keywords   - list:str  - if any reports contain any of these words, run mali(). empty list to disable  
    # mali_if_all_match     - bool      - only run mali() if all criteria match. if False, run if any criteria match

  # destructive
    # dest_account_age      - int       - if account is newer than X days, run dest(). -1 to disable
    # dest_report_count     - int       - if account has X or more reports, run dest(). -1 to disable
    # dest_match_keywords   - list:str  - if any reports contain any of these words, run dest(). empty list to disable  
    # dest_if_all_match     - bool      - only run dest() if all criteria match. if False, run if any criteria match


# reaction_report           - bool      - react to a user join message with:
#                                           💚 good account
#                                           👀 meets problematic criteria
#                                           🔶 meets malicious criteria
#                                           🟥 meets destructive criteria


#################################
### TODO
#################################

#TODO implement settings per guild on yaml
#TODO set up git
#TODO git push data repo if local is ahead (local will be source of most up-to-date)
#TODO setup walkthrough of settings on first run in server. hidden bot messages in main channel to owner only?

#DONE load bad accts' yaml files into one large variable that can be searched