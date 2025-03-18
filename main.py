import discord
import asyncio
import random
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True

client = commands.Bot(command_prefix=';', self_bot=True, intents=intents)
TOKEN = 'x'

# Initialize data structures
emojis_per_user = {}
active_users = set()
chatpack_users = {}

# login
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name="xxx", url="https://twitch.tv/awududioaw"))
    print(f'Logged in as {client.user}')

# Emoji commands
@client.group()
async def emoji(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('invalid cmd')

@emoji.command(name='set')
async def emoji_set(ctx, *args):
    if not args:
        await ctx.send(';set :sob: @user')
        return

    potential_user = args[-1]
    try:
        user = await commands.UserConverter().convert(ctx, potential_user)
        emojis = args[:-1]
    except commands.BadArgument:
        await ctx.send('invalid user')
        return

    if not emojis:
        await ctx.send('no emojis')
        return

    emojis_per_user[user.id] = emojis
    await ctx.send(f"set emojis for {user.name}: {', '.join(emojis)}", delete_after=1)
    await asyncio.sleep(1)
    await ctx.message.delete()

@emoji.command(name='start')
async def emoji_start(ctx, user: discord.User):
    if user.id not in emojis_per_user:
        await ctx.send(f"No emojis set for {user.name}", delete_after=3)
        await asyncio.sleep(3)
        await ctx.message.delete()
        return

    active_users.add(user.id)
    await ctx.send(f"reacting to {user.name}", delete_after=1)
    await asyncio.sleep(1)
    await ctx.message.delete()

@emoji.command(name='stop')
async def emoji_stop(ctx, user: discord.User):
    active_users.discard(user.id)
    await ctx.send(f"Stopped reacting to {user.name}", delete_after=1)
    await asyncio.sleep(1)
    await ctx.message.delete()

# Banner command
@client.command(name='banner')
async def banner(ctx, user: discord.User):
    user = await client.fetch_user(user.id)
    banner_url = user.banner.url if user.banner else 'User has no banner.'
    await ctx.send(banner_url)

# Chatpack command
@client.command(name='chatpack')
async def chatpack(ctx, *args):
    if not args:
        await ctx.send('@user or off')
        return

    if args[0].lower() == 'off':
        if len(args) == 1 or args[1].lower() == 'all':
            chatpack_users.clear()
            await ctx.send('chatpack disabled', delete_after=1)
        else:
            try:
                target = args[1]
                user = await commands.UserConverter().convert(ctx, target)
                if user.id in chatpack_users:
                    del chatpack_users[user.id]
                    await ctx.send(f'packing {user.name}', delete_after=1)
                else:
                    await ctx.send(f'stopped packing {user.name}', delete_after=1)
            except commands.BadArgument:
                await ctx.send('no user found')
    else:
        try:
            target = args[0]
            user = await commands.UserConverter().convert(ctx, target)
            with open('responses.txt', 'r') as file:
                responses = [line.strip() for line in file.readlines()]
            chatpack_users[user.id] = responses
            await ctx.send(f'packing {user.name}', delete_after=1)
        except commands.BadArgument:
            await ctx.send('invalid user')

    await asyncio.sleep(1)
    await ctx.message.delete()

# DM clear command
@client.command(name='cleardm')
async def cleardm(ctx):
    if ctx.guild is None:
        def is_self(m):
            return m.author == client.user

        deleted = await ctx.channel.purge(limit=None, check=is_self)
        await ctx.send(f'Deleted {len(deleted)} message(s)', delete_after=3)
        await asyncio.sleep(3)
        await ctx.message.delete()

# Avatar command
@client.command(name='avatar')
async def avatar(ctx, user: discord.User):
    await ctx.send(user.avatar_url)

# Message event
@client.event
async def on_message(message):
    global emojis_per_user, active_users, chatpack_users

    if message.author.id in active_users:
        emojis = emojis_per_user.get(message.author.id, [])
        for emoji in emojis:
            await message.add_reaction(emoji)

    if message.author.id in chatpack_users:
        responses = chatpack_users[message.author.id]
        response = random.choice(responses)
        await message.reply(response, mention_author=True)

    await client.process_commands(message)

client.run(TOKEN, bot=False)
