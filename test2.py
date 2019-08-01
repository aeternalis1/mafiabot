import discord
import random

client = discord.Client()

activity = discord.Game(name="m!help")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=activity)


commands = {
    'help': '`m!help` displays the help screen. Fairly obvious.',
    'h2p': '`m!h2p` describes the basic rules and premise of the game.',
    'start': '`m!start` begins a new round of mafia.',
    'end': '`m!end` ends the current game, if existing. Can only be called by a moderator or a player.',
    'roles': '`m!roles` lists all available roles that can be added to the game.',
    'set': '`m!set [role] [number]` set the quantity of `[role]` in the setup to `[number]`. e.g. `m!set villager 3`',
    'setup': '`m!setup` shows the full complement of roles in the current setup.',
    'settings': '`m!settings` displays all the settings of the current game.',
    'toggle': '`m!toggle [setting]` flips `[setting]` from on to off, or vice versa. Type `m!settings` to see options. e.g. `m!toggle daystart`',
    'setlimit': '`m!setlimit [phase] [time]` sets the time limit for `[phase]` to `[time]` in minutes. `[time]` can be a positive real number at least 1 or `inf`. e.g. `m!setlimit day 10`',
    'join' : '`m!join` adds you to the game.',
    'leave' : '`m!leave` removes you from the game. This may end an ongoing game, so be careful using this command.',
    'vote': '`m!vote [player]` puts your current vote on `player`. Vote this bot to set your vote to no-lynch, which will instantly end the day if in majority. e.g. `m!vote @mafiabot`', # <------ get id of bot and put here
    'unvote': '`m!unvote` sets your vote to nobody (no vote).',
    'status': '`m!status` displays all players and their votes, as well as the vote count on each player.',
    'players': '`m!players` displays all players who are currently alive',
    'alive': '`m!alive` displays all the roles and their quantities that are still in play.'
}


help_text = [
    "```List of commands```",
    "Type `m!help [command]` to receive details about the command itself.",
    "**1. Basic**: `help` `h2p` `start` `end`",
    "**2. Setup**: `roles` `set` `setup` `settings` `toggle` `setlimit` `join` `leave`",
    "**3. In-game**: `vote` `unvote` `status` `players` `alive`"
]


h2p_text = [
    "**How to play:**",
    "Mafia is a party game in which all the players are split into two opposing factions: the innocent villagers and the guilty mafia.\n",
    "The game alternates between two phases:",
    "1. Daytime, when players can discuss and debate the identity of the mafia. Players can also majority vote to lynch one member of the community who they suspect of being guilty.",
    "2. Nighttime, when mafia are free to murder one innocent citizen of the town, and certain townspeople can use their special abilities.\n",
    "If you are a villager, your win condition is to identify and lynch all of the mafia.",
    "If you are a mafia, your win condition is to either equal or outnumber the townspeople.",
    "At the start of the game, your role will be assigned to you via DM by this bot.\n",
    "NOTE: It is recommended to mute pings from this bot, since `@'s` are necessary to properly identify players."
]


roles_text = [
    "**Roles:**",
    "`villager`: Village-aligned role. No special powers.",
    "`normalcop`: Village-aligned role, capable of determining the alignment of a target player during nighttime.",
    "`paritycop`: Village-aligned role, capable of determining whether his LAST TWO targets are of the same alignment.",
    "`doctor`: Village-aligned role, capable of saving a target player from death during nighttime.",
    "`mafia`: Mafia-aligned role. Capable of killing a villager during nighttime with fellow mafia."
]


toggle_text = [{
    'daystart': '`daystart` toggled off: The game will commence during nighttime.',
    'selfsave': '`selfsave` toggled off: The doctor will not be able to save himself during nighttime.',
    'conssave': '`conssave` toggled off: The doctor will not be able to save the same patient over consecutive nights.',
    'continue': '`continue` toggled off: The game will end if a living player quits.',
    'reveal': '`reveal` toggled off: When a player dies, their role will not be revealed.'
}, {
    'daystart': '`daystart` toggled on: The game will commence during daytime.',
    'selfsave': '`selfsave` toggled on: The doctor will be able to save himself during nighttime.',
    'conssave': '`conssave` toggled on: The doctor will be able to save the same patient over consecutive nights.',
    'continue': '`continue` toggled on: The game will not end if a living player quits.',
    'reveal': '`reveal` toggled on: When a player dies, their role will be revealed.'
}]


end_text = {
    'None': 'Nobody wins!',
    'Mafia': 'The mafia win!',
    'Town': 'The villagers win!'
}


class Player:
    def __init__(self, id, server):
        self.id = id
        self.alive = 1
        self.role = None
        self.vote = None
        self.server = server
        self.ingame = 1         # changes to 0 upon m!leave, will be removed from server.players upon game end


class Server:
    def __init__(self):
        self.players = {}       # dictionary mapping player IDs to a Player class
        self.game = {
            'running': 0,
            'phase': 0
        }
        self.settings = {
            'daystart': 0,      # game starts during daytime
            'selfsave': 0,      # doctor can save themselves
            'conssave': 0,      # doctor can save the same person in consecutive turns
            'continue': 0,      # continue playing even if a player leaves
            'reveal': 0,        # reveal role of player upon death
            'limit1': 'inf',    # time limit for days
            'limit2': 'inf'     # time limit for nights
        }
        self.setup = {
            'villager': 0,
            'normalcop': 0,
            'paritycop': 0,
            'doctor': 0,
            'mafia': 0
        }


players = {}        # dictionary mapping player IDs to alive/dead status (1 for alive, 0 for dead), init to 1 when m!join or end of last game
                    # player will be removed upon m!leave

roles = {}          # dictionary mapping player IDs to roles (as strings)
                    # all players will be removed upon game end (and reset next game)

votes = {}          # dictionary mapping player IDs to votes (other player IDs, or None)
                    # player will be removed upon death

servers = {}        # dictionary mapping server IDs to server class
                    # new server class will be created whenever bot is run in server

allPlayers = {}     # dictionary mapping player IDs to server they're playing in


async def death(message, author, server):
    await message.channel.send('<@%s> has died. Their role was %s.' % (author, roles[author]))


async def gameEnd(message, winner, server):     # end of game message (role reveal, congratulation of winners)
    server.game['running'] = 0
    await message.channel.send('\n'.join([end_text[winner]] + ['The roles were as follows:'] + ['<@%s> : `%s`' % (player.id, player.role) for player in server.players.values()]))
    for player in server.players.values():
        player.role = None


async def invalid(message, server):
    await message.channel.send('Invalid request. Please refer to `m!help` for aid.')


async def m_help(message, author, server):
    query = message.content.split()
    if len(query) == 1:
        await message.channel.send('\n'.join(help_text))
    elif len(query) == 2 and query[1] in commands:
        await message.channel.send(commands[query[1]])
    else:
        await invalid(message)


async def m_h2p(message, author, server):
    await message.channel.send('\n'.join(h2p_text))


async def m_start(message, author, server):
    if server.game['running']:
        await message.channel.send('The game is already ongoing.')
        return

    '''
    if sum([val for val in server.setup.values()]) != sum([player.ingame for player in server.players.values()]):
        await message.channel.send('The number of roles does not match the number of players!')
        return
    if sum([val for val in server.setup.values()]) / 2 <= server.setup['mafia']:
        await message.channel.send('The setup is invalid. Mafia cannot start with half of or more than half of the total number of players.')
        return
    if server.setup['mafia'] == 0:
        await message.channel.send('The setup is invalid. There must be at least one mafia in the game.')
        return
    '''

    # distribution of roles
    allRoles = []
    for key in server.setup:
        allRoles = allRoles + [key] * server.setup[key]
    random.shuffle(allRoles)
    for player in server.players.values():
        role = allRoles.pop()
        player.role = role
        user = await client.fetch_user(str(player.id))
        await user.send('Your role is `%s`.' % role)

    if server.settings['daystart']:
        server.game['phase'] = 1
    server.game['running'] = 1
    await message.channel.send('The game has begun!')


async def m_end(message, author, server):   # can only end game if currently playing (alive) or server mod/admin
    await gameEnd(message, 'None', server)


async def m_roles(message, author, server):
    await message.channel.send('\n'.join(roles_text))


async def m_set(message, author, server):
    if server.game['running']:
        await message.channel.send('Game is ongoing.')
        return
    query = message.content.split()
    if query[1] not in server.setup or len(query) < 3:
        await invalid(message)
        return
    try:
        num = float(query[2])
    except ValueError:
        await invalid(message)
        return
    if num != int(num):
        await message.channel.send('Invalid input: inputted quantity must be integer.')
    elif num < 0:
        await message.channel.send('Invalid input: inputted quantity cannot be negative.')
    else:
        num = int(num)
        server.setup[query[1]] = num
        await message.channel.send('Successfully changed the number of `%ss` in the setup to `%d`.' % (query[1], num))


async def m_setup(message, author, server):
    if not sum([val for val in server.setup.values()]):
        await message.channel.send('There are currently no roles in the setup. Use `m!set [role] [number]` to add some!')
        return
    await message.channel.send('\n'.join(['The setup consists of:'] + [key + ': ' + str(server.setup[key]) for key in server.setup if server.setup[key]]))


async def m_settings(message, author, server):
    msg = ['%s : %d - %s' % (key, server.settings[key], toggle_text[server.settings[key]][key]) for key in toggle_text[0]]
    msg += ['Time limit for %s is %s minute(s).' % (['days', 'nights'][x - 1], server.settings['limit' + str(x)]) for x in [1, 2]]
    await message.channel.send('\n'.join(msg))


async def m_toggle(message, author, server):
    if server.game['running']:
        await message.channel.send('Game is ongoing.')
        return
    query = message.content.split()
    if query[1] in server.settings:
        server.settings[query[1]] ^= 1
        await message.channel.send(toggle_text[server.settings[query[1]]][query[1]])
    else:
        await invalid(message)


async def m_setlimit(message, author, server):
    if server.game['running']:
        await message.channel.send('Game is ongoing.')
        return
    query = message.content.split()
    if query[2] == 'inf':
        if query[1] == 'day':
            server.settings['limit1'] = 'inf'
            await message.channel.send('Time limit for day set to infinite minutes.')
        else:
            server.settings['limit2'] = 'inf'
            await message.channel.send('Time limit for night set to infinite minutes.')
    else:
        try:
            lim = float(query[2])
            if lim < 1:                # time limit must be at least 1 minute
                await invalid(message)
                return
            if query[1] == 'day':
                server.settings['limit1'] = lim
                await message.channel.send('Time limit for day set to ' + query[2] + ' minutes.')
            else:
                server.settings['limit2'] = lim
                await message.channel.send('Time limit for night set to ' + query[2] + ' minutes.')
        except ValueError:
            await invalid(message)


async def m_join(message, author, server):
    if server.game['running']:
        await message.channel.send('Game is ongoing.')
        return
    if author in server.players:
        await message.channel.send('<@%s>, you are already in the game!' % str(author))
    elif author in allPlayers:
        await message.channel.send('<@%s>, you cannot be in more than one game at a time!' % str(author))
    else:
        allPlayers[author] = message.guild
        server.players[author] = Player(author, server)
        await message.channel.send('<@%s> has joined the game.' % str(author))


async def m_leave(message, author, server):
    if author not in allPlayers or allPlayers[author] != message.guild:     # not server they're playing in
        await message.channel.send('<@%s>, you are not currently part of the game in this server.' % str(author))
        return
    if server.game['running'] and author in server.players:
        if server.players[author].alive:
            await message.channel.send('<@%s> has elected to leave the game.' % str(author))
            server.players[author].alive = 0
            server.players[author].ingame = 0
            if server.settings['continue']:
                await death(author)
            else:
                server.game['running'] = 0
                await gameEnd(message, 'None', server)
        else:
            pass
            # player quits (leaves text and voice channels, loses role)
        return
    if author not in server.players:
        await message.channel.send('<@%s>, you were not in the game to begin with!' % str(author))
    else:
        server.players.pop(author)
        allPlayers.pop(author)
        await message.channel.send('<@%s> has left the game.' % str(author))


async def m_vote(message, author, server):
    if not server.game['running']:
        await message.channel.send('The game has not yet started. Don\'t be so hasty to vote!')
        return
    if author not in server.players or not server.players[author].alive or not server.game['phase']:     # not playing, not alive, night
        await message.channel.send('You cannot vote!')
        return
    query = message.content.split()
    tar = query[1]
    try:
        if len(tar) <= 3 or tar[:2] != '<@' or tar[-1] != '>' or (int(tar[2:-1]) != client.user.id and int(tar[2:-1]) not in server.players) or (int(tar[2:-1]) in server.players and not server.players[int(tar[2:-1])].alive):
            await message.channel.send('That is an invalid voting target. Vote in the form `m!vote @user`, where user is a living player.')
            return
    except ValueError:
        await message.channel.send('That is an invalid voting target. Vote in the form `m!vote @user`.')
        return
    await message.channel.send('<@%s> has placed their vote on <@%s>.' % (str(author), str(tar[2:-1])))
    server.players[author].vote = int(tar[2:-1])


async def m_unvote(message, author, server):
    if not server.game['running']:
        await message.channel.send('The game has not yet started. There\'s nobody to unvote!')
        return
    if author not in server.players or not server.players[author].alive or not server.game['phase']:     # not playing, not alive, night
        await message.channel.send('You cannot change your vote at this time.')
        return
    server.players[author].vote = None
    await message.channel.send('<@%s> has removed their vote, and is now voting nobody.' % str(author))


async def m_status(message, author, server):
    if not server.game['running']:
        await message.channel.send('The game has not yet started. There are no votes in effect.')
        return
    if author not in server.players or not server.players[author].alive or not server.game['phase']:     # not playing, not alive, night
        await message.channel.send('Daytime is not in session. There are no votes in effect.')
        return
    num = sum([player.alive for player in server.players.values()])
    msg = ['The votes are currently as follows:']
    count = {}
    for player in server.players.values():
        if not player.alive:
            continue
        if player.vote == client.user.id:
            msg.append('<@%s> is currently voting for a no-lynch.' % str(player.id))
        elif player.vote == None:
            msg.append('<@%s> is currently voting for nobody.' % str(player.id))
        else:
            msg.append('<@%s> is currently voting <@%s>' % (str(player.id), player.vote))
            if player.vote not in count:
                count[player.vote] = 1
            else:
                count[player.vote] += 1
    count2 = {}
    for i in range(num+1):
        count2[i] = []
    for key in count:
        count2[count[key]].append(key)
    msg.append('Voting summary:')
    for i in range(num,-1,-1):
        if count2[i]:
            msg.append(str(i) + ' vote(s) on: ' + ', '.join(['<@%s>' % str(key) for key in count2[i]]))
    msg.append('No lynch: %d vote(s)' % sum([player.vote == client.user.id for player in server.players.values() if player.alive]))
    msg.append('Nobody: %d vote(s)' % sum([player.vote == None for player in server.players.values() if player.alive]))
    await message.channel.send('\n'.join([line for line in msg]))



async def m_players(message, author, server):
    num = sum([player.alive for player in server.players.values()])
    if not server.game['running']:
        if not num:
            await message.channel.send('There are currently no players in the game. Type `m!join` to join!')
        else:
            await message.channel.send(' '.join(['The following players are in the game:'] + ['<@%s>' % str(key) for key in server.players]))
        return
    await message.channel.send(' '.join(['The following players are alive:'] + ['<@%s>' % str(player.id) for player in server.players.values() if player.alive]))


async def m_alive(message, author, server):
    if not server.game['running']:
        await message.channel.send('There is no ongoing game. Use `m!setup` to see the current setup of the game.')
        return
    if not server.settings['reveal']:
        await message.channel.send('Remaining roles are unknown, due to the `reveal` setting being toggled off.')
    else:
        msg = ['Remaining roles are as follows:']
        msg += ['`%s` : %d' % (role, sum([player.role == role for player in server.players.values() if player.alive])) for role in server.setup]
        await message.channel.send('\n'.join(msg))


tofunc = {
    'help' : m_help,
    'h2p': m_h2p,
    'start': m_start,
    'end': m_end,
    'roles': m_roles,
    'set': m_set,
    'setup': m_setup,
    'settings': m_settings,
    'toggle': m_toggle,
    'setlimit': m_setlimit,
    'join': m_join,
    'leave': m_leave,
    'vote': m_vote,
    'unvote': m_unvote,
    'status': m_status,
    'players': m_players,
    'alive': m_alive
}


@client.event
async def on_message(message):
    if message.guild not in servers:
        servers[message.guild] = Server()
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'm!':
        return
    query = message.content[2:].split()
    if len(query) and query[0] in commands:
        func = tofunc[query[0]]
        await func(message, message.author.id, servers[message.guild])
    else:
        await invalid(message, servers[message.guild])



client.run('NTk0MTg0ODU4MTM4NTc0ODQ4.XUNO_w.BI96Lb3mHPQ2x_DPx2lggglSRIc')


'''
REMEMBER TO REMOVE TOKEN WHEN COMMITTING

REMINDERS:
- author returns integer


NOTES:
- Does it require a different instance of itself per server? How does this work with DM (if a person joins in two servers). 
    - Solution: make each player only capable of joining in a single distinct server
    - Keep a map servers = {} that stores the server ID for each player...?
    - Maybe allow voting in DMs? And bot can announce vote in main chat?
- REMEMBER TO DISTINGUISH BETWEEN COMMANDS YOU CAN USE IN DM AND COMMANDS YOU CAN'T

GAMEPLAY:

All players are initially in both a text channel and a voice chat, and upon gamestart will be DM'd a role by the bot.

Mafia members will be in a group DM, and upon death will be removed by the bot.
Doctor and cop will receive a prompt by the bot each night phase
 - Bot will list all living players (because you can't ping people not in the DM), and will prompt input of single integer
    - MAYBE USE THIS MECHANIC FOR NORMAL VOTING? TO AVOID PINGING OTHER PLAYERS
 - Normal cop cannot investigate himself, parity cop can, doctor can save himself if selfsave = 1, mafia cannot selfkill

Daytime discussion should primarily occur in VC, but players can use text channels if they want. Text channel will be used for voting and other in-game commands.



Nighttime will occur in DMs. The main text channel will be locked and nobody will be able to speak there (might need to end game? rethink this).
Graveyard text channel will be able to continue to talk.


'''
