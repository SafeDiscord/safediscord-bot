# https://pypi.org/project/discord-py-slash-command/
# https://discordpy.readthedocs.io/en/rewrite/index.html
# https://realpython.com/how-to-make-a-discord-bot-python/

import os
# import discord
# import git

# from discord.ext import commands
# from discord_slash import SlashCommand, SlashContext

from  dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# #################################
# ### load up yaml list of malicious accounts
# #################################

# # SD_repo = git.Repo('https://github.com/SafeDiscord/safediscord-repo.git')
# # SD_repo.remotes.origin.pull()
# # read YAML into var


# #################################
# ### set up client
# #################################


# bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
# slash = SlashCommand(bot)

# @bot.event
# async def on_ready():

#   print('Connecting to:')
#   for guild in bot.guilds:
#     print(' - ', guild.id, guild.name)
#     # get config file for the guild, use source or something, load file up as variables

# # @bot.event
# # async def on_member_join(member):
#   #check if UUID matches any from the YAML
  
#   #shim
#   # is_bad = True
  
#   # if is_bad:
#   #   if guild.sd_settings.send_in_channel:
#   #     guild.settings.warning_channel.send('looks like {member.name} has infractions')


# #################################
# ### utils
# #################################

# # does user have perms
# # async def have_cmd_perms(author):
# #   return True

# #################################
# ### set up commands
# #################################



# @slash.slash(name='check')
# @commands.has_role('admin') # change this to be based on settings yaml
# async def _check(ctx: SlashContext):
#   embed = discord.Embed(title="embed test")
#   await ctx.send(content='received', embed=[embed])




# bot.run(TOKEN)



# # guild settings
# # send_in_channel bool    - send warning messages in a specific channel
# # warning_channel string  - channel ID (not name) to send warning messages within 
# # role_required_for_cmd   - plaintext of lowest role required to run commands


import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot)

@slash.slash(name="test")
async def _test(ctx: SlashContext):
    embed = discord.Embed(title="embed test")
    await ctx.send(content="test", embeds=[embed])


bot.run(TOKEN)