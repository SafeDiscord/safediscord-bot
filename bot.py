# sources to read and learn about slash commands and  discord.py in general

# https://pypi.org/project/discord-py-slash-command/
# https://discordpy.readthedocs.io/en/rewrite/index.html
# https://realpython.com/how-to-make-a-discord-bot-python/

# import all th stuff needed later
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

#loads from a file called .env. I didn't push it because it contains a secret passcode token for the bot.
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

# creates a bot user, and sets it up with discord's slash commands intents
#TODO: narrow down list of intents https://discord.com/developers/docs/topics/gateway#list-of-intents
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

# as soon as bot is operational
@bot.event
async def on_ready():

  #iterate through guilds it's connected to
  print('Connecting to:')
  for guild in bot.guilds:
    print(' - ', guild.id, guild.name)

    # check if guild is a new one
    if not guild.id in saved_guilds:
      print('new guild! adding to config, hold tight.')

      #grab defaults, append it, safe to file
      saved_guilds[guild.id] = new_guild_defaults
      save_guilds(saved_guilds)

    for member in guild.members:
      # ignore members that are just other bots
      results = await check_member(member.id)
      
      if results:
        print(f'Results found for {member.name}')

# when a new member joins
@bot.event
async def on_member_join(member):
  #check if UUID matches any from the YAML
  results = await check_member(member.id)

  if results:
    owner_dm = await member.guild.owner.create_dm()
    embed = await create_embed(results)
    await owner_dm.send(embed=embed)
    


#################################
# util functions
#################################

#create embeds
async def create_embed(results):

  #grab user from discord's API even if left server
  user = await bot.fetch_user(results['_id'])

  #create new embed
  embed = discord.Embed(
    title=f"Report for {user}",
    color=discord.Color(0x3e038c), #TODO set color based on threshold
  )

  embed.set_thumbnail(url=user.avatar_url)

  # + "\n\u200b" adds a single newline below the current line, for spacing. 
  # https://github.com/Rapptz/discord.py/issues/643 
  embed.add_field(
    name=f'Report Count:', value=f'{results["report_count"]}' + "\n\u200b", inline=False)
  
  #iterate through the reports, only insert the first 3
  for report in results['reports'][:3]:
    embed.add_field(name=f'Date:', value=report['date'], inline=True)
    embed.add_field(name=f'Server:', value=report['server_name'], inline=True)
    embed.add_field(name=f'Message:', value=report['report_msg'] + "\n\u200b", inline=False)

  #if there were no reports, 
  if results["report_count"] == 0:
    embed.add_field(name='** **', value=f'Clean slate!')
  
  #otherwise if there were more than 3 reports
  elif results["report_count"] > 3:
    embed.add_field(name='** **', value=f'... plus {results["report_count"] - 3} more')

  return embed
  

# is member bad
async def check_member(_id):

  #grab user from discord's API even if left server
  user = await bot.fetch_user(_id)

  if user.bot:
    return False

  # send positive report if no reports
  if not _id in reports:
    return {"report_count":0, "_id":_id,"reports":[],"threshold":0}
  
  # get report count, and threshold
  report_count = reports[_id]['report_count']
  threshold = "warn" 

  return {
    "report_count":report_count, 
    "_id":_id, 
    "threshold":threshold, 
    "reports":reports[_id]['reports']
  }


#################################
# set up commands
#################################

@slash.slash(
  name="check", 
  description="Check if a user is in the reports database", 
  options=[ 
    create_option(
      name="user",
      description="Tag user to check",
      option_type=6,
      required=True
    )
  ])
async def _check(ctx, user: discord.User):

  # if user is int instead of discord User, 
  # grab the user based on int (id) from discord API
  if isinstance(user, int):
    user = await bot.fetch_user(user)
  
  # grab report
  results = await check_member(user.id)
  if results:
    embed = await create_embed(results)
    await ctx.send(embed=embed, hidden=True)
  
# same thing as above, except no `hidden=True`,
# so all server users can see the message, not just the cmd user
@slash.slash(
  name="show", #TODO replace show with an optional visible flag within check
  description="Same as /check, shows results in chat for everyone",
  options=[
    create_option(
      name="user",
      description="Tag user to check",
      option_type=6,
      required=True
    )
  ])
async def _show(ctx, user: discord.User): #same as above
  if isinstance(user, int):
    user = await bot.fetch_user(user)

  results = await check_member(user.id)
  if results:
    embed = await create_embed(results)
    await ctx.send(embed=embed)
 


@slash.slash(
  name="report", 
  description="Report user to Safe Discord database",
  options=[ 
    # the two options create two params that are both required, in this order
    create_option(
      name="user",
      description="Tag user to report",
      option_type=6,
      required=True
    ),
    create_option(
      name="report",
      description="Description of report",
      option_type=3,
      required=True
    )
  ])
async def _report(ctx, user:discord.User, report):

  # this should be mentally taxing because it is a permanent record
  # don't want it to be too easy and then have people submitting joke reports 
  # requiring confirmation is a good idea.
  # is it a good idea to ask 2 others to confirm?
  # let the owner or account set up to be in charge set up a role for confirmation
  # and then ping the role and go for 2 confirmations, store those inside the same report
  # each confirmation is its own command. 
  
  # on report:
     # check if user has settings.submit_rank role within guild for report
        # if no role:
          # ctx.send you do not have enough permissions to submit a report 
     
      # bot stores report contents, timestamp, submitted ID, guild ID
      # PM settings.confirm_rank with stored report info, ask to confirm within settings.report_confim_time

  
  # on report cofirmation:
      # check if user has settings.confirm_rank role within guild for report
        # if no role:
          # ctx.send you do not have enough permissions to confirm a report 
      
      # check first argument for report keywords (pineapple-football-eight, PAKE-like?)
        # if does not exist:
          # ctx.send report with that ID does not exist
      
      # check report timestamp vs current timestamp
        # if difference is more than settings.report_confirm_time:
          # ctx.send report is out of date. Please submit new report
      
      # add to report that one confirmation has gone through
      # ctx.send confirmation sent! thank you for your honesty and help keeping discord safer



# /report submit @user message description
# /report confirm report ID (autofill?) message description

# /check @user
# /check @user visible


  await ctx.send(content="Report added! :white_check_mark: (dry run cmd)", hidden=True)


bot.run(TOKEN)



#################################
### settings for later date
#################################

### general channel and role settings
  # warn_in_server            - bool      - send warning messages in a server? otherwise PM owner
  # warn_in_server_channel    - int       - channel to send warning messages within 

  # check_rank                - role      - lowest role required to run check cmd
  # report_rank               - role      - lowest role required to send reports
  # confirm_rank              - role      - lowest role required to confirm reports
  
  # require_confirm           - bool      - require confirmation for reports? otherwise send immediately
  # confirm_in_server         - bool      - allow confirmation cmd within server? otherwise send PMs to settings.confirm_rank
  # confirm_in_server_channel - int       - channel to allow confirmation cmd. If `-1` cmd allowed anywhere

  # check_in_server           - bool      - allow check to be ran within server? otherwise only in PMs to bot

  # report_on_join            - bool      - run reports on people joining?
  # report_on_join_channel    - int       - channel to send automatic reports on user join
  # pm_report_on_join         - bool      - PM settings.pm_report_on_join_rank with report on join? 
  # pm_report_on_join_rank    - int       - role that gets PMd with reports on user join

  
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

