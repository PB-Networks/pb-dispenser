import discord
from discord.ext import commands
import httpx
import re
import random
import subprocess
import sys
import sympy
import asyncio
from collections import defaultdict
from datetime import datetime


user_usage_count = defaultdict(int)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='p!', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Coming Soon | by Devman"))
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.guild is None and not message.author.bot:  
        if not message.content.startswith('p!avatar'):  
            return
    await bot.process_commands(message)

@bot.command(name='ban') # Ban someone
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban someone"""
    await member.ban(reason=reason)
    await ctx.send(f'{member.display_name} has been banned.')

@bot.command(name='kick') # Kick someone
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick someone"""
    await member.kick(reason=reason)
    await ctx.send(f'{member.display_name} has been kicked.')

@bot.command(name='timeout') # Timeout someone
async def timeout(ctx, member: discord.Member, duration: int, *, reason=None):
    """Timeout a user as a punishment"""
    role = discord.utils.get(ctx.guild.roles, name='Timeout') 
    await member.add_roles(role, reason=reason)
    await ctx.send(f'{member.display_name} has been timed out for {duration} seconds.')

    await asyncio.sleep(duration)
    await member.remove_roles(role)

@bot.command(name='mute') # Mute someone
async def mute(ctx, member: discord.Member, *, reason=None):
    """Mute a member in the server"""
    role = discord.utils.get(ctx.guild.roles, name='Muted')  
    await member.add_roles(role, reason=reason)
    await ctx.send(f'{member.display_name} has been muted.')

@bot.command(name='ping') # checks the bot's latency
async def ping(ctx):
    """Check the bot's latency"""
    latency = round(bot.latency * 1000)  
    await ctx.send(f'Pong! Latency: {latency}ms')

@bot.command(name='findrepo') # Find a github repo that you can't find by using this command
async def find_repo(ctx, search_query):
    """Find a Github repo easily"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://api.github.com/search/repositories?q={search_query}')
        if response.status_code == 200:
            search_results = response.json()['items']
            if search_results:
                result_index = random.randint(0, len(search_results) - 1)
                result = search_results[result_index]
                await ctx.send(f'Repo found! Name: {result["full_name"]}, URL: {result["html_url"]}')
            else:
                await ctx.send('No repositories found for the given query.')
        else:
            await ctx.send(f'Error searching GitHub repositories: {response.status_code}')

@bot.command(name='cmds') # see all the commands
async def cmds(ctx):
    """Shows all the commands"""
    commands_list = '\n'.join([f'`!{command.name}` - {command.help}' for command in bot.commands])

    embed = discord.Embed(
        title='Bot Commands',
        description=commands_list,
        color=discord.Color.blue()
    )

    embed.set_footer(text=f'Use {bot.command_prefix}help for more details on a specific command and make sure to use p!thecommand')

    await ctx.send(embed=embed)

@bot.command(name='avatar') # Get your avatar
async def avatar(ctx, user: discord.User = None):
    """Get the avatar of a user"""
    target_user = user or ctx.author
    avatar = target_user.avatar
    await ctx.send(f'Avatar of {target_user.display_name}: {avatar}')

@bot.command(name='dm') # Dm people by the bot
async def dm(ctx, member: discord.Member, *, message):
    """DMs a member (Only if they have dm enabled)"""
    try:
        await member.send(message)
        await ctx.send(f'Message successfully sent to {member.display_name}')
    except discord.Forbidden:
        await ctx.send(f"Unable to send message to {member.display_name}. User may have DMs disabled or blocked the bot.")

@bot.command(name='invite') # link to invite the bot
async def invite(ctx):
    """Invite the bot to your server"""
    permissions = discord.Permissions(send_messages=True, read_messages=True)
    invite_link = discord.utils.oauth_url(bot.user.id, permissions=permissions)
    embed = discord.Embed(description=f'You can invite the bot to your server using the following link: {invite_link}', color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name='image') # make it easier to find picture by using this command
async def image(ctx, *, query):
    """Searches for an image on Google and sends it as a message"""
    search_url = f'https://www.google.com/search?tbm=isch&q={query}'
    await ctx.send(f'Here are the Google image search results for {query}: {search_url}')

@bot.command(name='setprefix') # Set the bot prefix like its ! and then you can change it to like anything
async def setprefix(ctx, new_prefix):
    """Set any custom prefix for the bot"""
    allowed_users = ['1074222869162250281', '1002565312681611354']  

    if str(ctx.author.id) in allowed_users:
        bot.command_prefix = new_prefix
        await ctx.send(f'Custom prefix set to: {new_prefix}')
    else:
        await ctx.send('You are not authorized to use this command.')

@bot.command(name='rate') # Rate yourself or others
async def rate(ctx, person):
    """Rate someone or yourself"""
    rating = random.randint(1, 10)  
    await ctx.send(f'I would rate {person} a {rating}/10!')

@bot.command(name='say') # Make the bot say anything
async def say(ctx, *, message):
    """Makes the bot say anything"""
    if 'n word' not in message.lower():
        await ctx.send(message)
    else:
        await ctx.send("I cannot say that word.")

@bot.command(name='stats') # check servers stats
async def stats(ctx):
    """Check the server stats"""
    total_members = len(ctx.guild.members)
    total_channels = len(ctx.guild.channels)
    total_text_channels = len(ctx.guild.text_channels)
    total_voice_channels = len(ctx.guild.voice_channels)
    
    embed = discord.Embed(
        title='Bot Statistics',
        description=f'Total Members: {total_members}\nTotal Channels: {total_channels}\nTotal Text Channels: {total_text_channels}\nTotal Voice Channels: {total_voice_channels}',
        color=discord.Color.dark_blue()
    )

    await ctx.send(embed=embed)

@bot.command(name='statsuser') # check someone's stats
async def statsuser(ctx, user: discord.Member):
    """Check someone's stats"""
    user_roles = ', '.join([role.name for role in user.roles])
    
    embed = discord.Embed(
        title=f'Statistics for {user.display_name}',
        description=f'User ID: {user.id}\nJoined at: {user.joined_at}\nRoles: {user_roles}',
        color=discord.Color.dark_blue()
    )

    await ctx.send(embed=embed)

@bot.command(name='newactivity') # U can change the activity
async def newactivity(ctx, *, new_activity):
    """Change the bot activity to anything"""
    allowed_users = ['1074222869162250281', '1002565312681611354'] 
    if str(ctx.author.id) in allowed_users:
        await bot.change_presence(activity=discord.Game(name=new_activity))
        await ctx.send(f'Activity changed to: {new_activity}')
    else:
        await ctx.send('You are not authorized to use this command.')

@bot.command() # You can use this command to restart the bot if any issue or if you updated and added new commands
async def re(ctx):
    """Restarts the bot"""
    await ctx.send("Restarting...")
    python = sys.executable
    subprocess.Popen([python, "main.py"])
    sys.exit()


links = ["NO LINKS YET", "NO LINKS YET", "NO LINKS YET"] # Links add as many as you want

@bot.command()  # This command allows you to generate links that you have added to the code up there!
async def gen(ctx):
    """Gen Proxy links"""
    if len(links) == 0:
        await ctx.send("No links added yet.")
        return

    if ctx.author.dm_channel is None:
        await ctx.author.create_dm()

    
    today = datetime.utcnow().date()
    if user_usage_count[str(ctx.author.id)] >= 3:
        await ctx.send("You have already used this command 3 times today. Please try again tomorrow.")
        return

    link = random.choice(links)
    embed = discord.Embed(title="Here is your link. Don't leak it or you will be banned from the bot", description=link, color=discord.Color.blue())

    await ctx.author.dm_channel.send(embed=embed)

    
    user_usage_count[str(ctx.author.id)] += 1

    
    confirmation = await ctx.send(f"I've sent the link to your DM. Click [Jump To The Message](https://discord.com/channels/{ctx.guild.id}/{ctx.author.dm_channel.id}) to view.")
    await asyncio.sleep(5)
    await confirmation.delete()

@bot.command() # U can use this command diff ways one way like a normal discord bot 2nd way is to lock it forever !lock f (which locks it forever)
async def lock(ctx, duration='f'):
      """Locks channel for a specified duration (default: forever)"""
      if duration == 'f':
          await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
          await ctx.send('Channel locked forever.')
      else:
          try:
              duration_seconds = int(duration)
              await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
              await ctx.send(f'Channel locked for {duration_seconds} seconds.')
              await asyncio.sleep(duration_seconds)
              await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
              await ctx.send('Channel unlocked.')
          except ValueError:
              await ctx.send('Invalid duration. Please specify a number of seconds or use "f" for forever.')

@bot.command() # Unlock the channel that you locked
async def unlock(ctx):
 """Unlocks the channel that you locked."""
 await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
 await ctx.send('Channel unlocked.')


bot.run('')
