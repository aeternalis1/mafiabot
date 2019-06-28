import discord

client = discord.Client()

activity = discord.Game(name="Mafioso")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=activity)


help_text = [
"```List of commands```",
"Type t!help [command] to receive details about the command itself.",
"**1. Basic**: `help` `h2p` `start` `end`"
"**2. Setup**: `roles` `add` `remove` `setup`"
"**3. In-game**: `vote` `unvote`"
]


async def m_help(message):
    for i in help_text:
        await message.channel.send(i)


def m_h2p():
    pass



@client.event
async def on_message(message):
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'm!':
        return
    command = message.content[2:]
    if command == 'help':
        await m_help(message)
    elif command == 'h2p':
        await m_h2p(message)



client.run('NTk0MTg0ODU4MTM4NTc0ODQ4.XRYvzw._Y6KIxJ0G9BpKd6ORpj2Uhtpmpg')