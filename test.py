import discord

client = discord.Client()

activity = discord.Game(name="Mafioso")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=activity)


help_text = [
"```List of commands```",
"Type t!help [command] to receive details about the command itself.",
"**1. Basic**: `help` `h2p` `start` `end`",
    # refers to itself, how to play, start game, end game (only mod or player)
"**2. Setup**: `roles` `add` `remove` `setup` `settings` `toggle`",
    # see all roles, add/remove role, check current setup
"**3. In-game**: `vote` `unvote` `status` `players` `alive`"
    # vote [player], unvote, who is voting whom, alive players, alive roles
]


commands = {
    'help': '`m!help` displays help screen. Fairly obvious.',
    'h2p': '`m!h2p` describes basic rules and premise of the game.',
    'start': '`m!start` begins a new round of mafia.',
    'end': '`m!end` ends the current game, if existing. Can only be called by a moderator or a player.',
    'roles': '`m!roles` lists all available roles that can be added to the game.',
    'add': '`m!add [role] [number]` adds `[number]`x of `[role]` to the current setup.',
    'remove': '`m!remove [role] [number]` removes `[number]`x of [role] from the current setup.',
    'setup': '`m!setup` shows the full complement of roles in the current setup.',
    'settings': '`m!settings` displays all the settings of the current game.',
    'toggle': '`m!toggle [setting]` flips `[setting]` from true to false, or vice versa. Do `m!settings` to see options',
    'vote': '`m!vote [player]` puts your current vote on `player`.',
    'unvote': '`m!unvote` sets your vote to nobody (no vote).',
    'status': '`m!status` displays all players and their votes, as well as current voting leaders.',
    'players': '`m!players` displays all players who are currently alive',
    'alive': '`m!alive` displays all the roles and their quantities that are still in play.'
}


async def invalid(message):
    await message.channel.send('Invalid request. Please refer to `m!help` for aid.')

async def m_help(message):
    query = message.content.split()
    if len(query) == 1:
        await message.channel.send("\n".join(help_text))
    elif len(query) == 2 and query[1] in commands:
        await message.channel.send(commands[query[1]])
    else:
        await invalid(message)

async def m_h2p(message):
    pass

async def m_start(message):
    pass

async def m_end(message):
    pass

async def m_roles(message):
    pass

async def m_add(message):
    pass

async def m_remove(message):
    pass

async def m_setup(message):
    pass

async def m_settings(message):
    pass

async def m_toggle(message):
    pass

async def m_vote(message):
    pass

async def m_unvote(message):
    pass

async def m_status(message):
    pass

async def m_players(message):
    pass

async def m_alive(message):
    pass


tofunc = {
    'help' : m_help, 'h2p': m_h2p, 'start': m_start,
    'end': m_end, 'roles': m_roles, 'add': m_add,
    'remove': m_remove, 'setup': m_setup, 'settings': m_settings,
    'toggle': m_toggle, 'vote': m_vote, 'unvote': m_unvote,
    'status': m_status, 'players': m_players, 'alive': m_alive
}


@client.event
async def on_message(message):
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'm!':
        return
    query = message.content[2:].split()
    if len(query) and query[0] in commands:
        func = tofunc[query[0]]
        await func(message)
    else:
        await invalid(message)





client.run('NTk0MTg0ODU4MTM4NTc0ODQ4.XRYvzw._Y6KIxJ0G9BpKd6ORpj2Uhtpmpg')