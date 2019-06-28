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
"**2. Setup**: `roles` `add` `remove` `setup`",
    # see all roles, add/remove role, check current setup
"**3. In-game**: `vote` `unvote` `status` `players` `alive`"
    # vote [player], unvote, who is voting whom, alive players, alive roles
]


commands = {
    'help': '`m!help` displays help screen. Fairly obvious.',
    'h2p': '`m!h2p` describes basic rules and premise of the game.',
    'start': '`m!start` begins a new round of mafia.',
    'end': '`m!end` ends the current game, if existing. Can only be called by a moderator or a player.',
    'roles': '`m!roles` lists all possible roles that can be added to the game.',
    'add': '`m!add [role] [number]` adds `[number]`x of `[role]` to the current setup.',
    'remove': '`m!remove [role] [number]` removes `[number]`x of [role] from the current setup.',
    'setup': '`m!setup` shows the full complement of roles in the current setup.',
    'vote': '`m!vote [player]` puts your current vote on `player`.',
    'unvote': '`m!unvote` sets your vote to nobody (no vote).',
    'status': '`m!status` displays all players and their votes, as well as current voting leaders.',
    'players': '`m!players` displays all players who are currently alive',
    'alive': '`m!alive` displays all the roles and their quantities that are still in play.'
}


async def m_help(message):
    await message.channel.send("\n".join(help_text))


def m_h2p():
    pass


@client.event
async def on_message(message):
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'm!':
        return
    command = message.content[2:].strip()
    if command == 'help':
        await m_help(message)
    elif command[:4] == 'help':
        command = command[5:].strip()
        if command in commands:
            await message.channel.send(commands[command])
        else:
            await message.channel.send('Invalid request. Please refer to `m!help`.') # <- make this a function?
    elif command == 'h2p':
        await m_h2p(message)



client.run('NTk0MTg0ODU4MTM4NTc0ODQ4.XRYvzw._Y6KIxJ0G9BpKd6ORpj2Uhtpmpg')