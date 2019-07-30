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


settings = {
    'daystart': 0,      # game starts during daytime
    'selfsave': 0,      # doctor can save themselves
    'conssave': 0,      # doctor can save the same person in consecutive turns
    'continue': 0,      # continue playing even if a player leaves
    'reveal': 0,        # reveal role of player upon death
    'limit1': 'inf',    # time limit for days
    'limit2': 'inf'     # time limit for nights
}


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


game = {
    'running': 0,
    'phase': 0      # phase of 0 for night, 1 for day
}

players = {}        # dictionary mapping player IDs to alive/dead status (1 for alive, 0 for dead), init to 1 when m!join or end of last game
                    # player will be removed upon m!leave

roles = {}          # dictionary mapping player IDs to roles (as strings)
                    # all players will be removed upon game end (and reset next game)

votes = {}          # dictionary mapping player IDS to votes (other player IDs, or None)
                    # player will be removed upon death


setup = {
    'villager': 0,
    'normalcop': 0,
    'paritycop': 0,
    'doctor': 0,
    'mafia': 0
}


async def death(message):
    await message.channel.send('<@%s> has died. Their role was %s.' % (message.author.id, roles[message.author.id]))


async def gameEnd(message, winner):     # end of game message (role reveal, congratulation of winners)
    game['running'] = 0
    await message.channel.send('\n'.join([end_text[winner]] + ['The roles were as follows:'] + ['<@%s> : `%s`' % (key, roles[key]) for key in roles]))
    roles.clear()


async def invalid(message):
    await message.channel.send('Invalid request. Please refer to `m!help` for aid.')


async def m_help(message):
    query = message.content.split()
    if len(query) == 1:
        await message.channel.send('\n'.join(help_text))
    elif len(query) == 2 and query[1] in commands:
        await message.channel.send(commands[query[1]])
    else:
        await invalid(message)


async def m_h2p(message):
    await message.channel.send('\n'.join(h2p_text))


async def m_start(message):
    if game['running']:
        await message.channel.send('The game is already ongoing.')
        return
    if sum([setup[key] for key in setup]) != sum([players[key] for key in players]):
        await message.channel.send('The number of roles does not match the number of players!')
        return
    if sum([setup[key] for key in setup]) / 2 <= setup['mafia']:
        await message.channel.send('The setup is invalid. Mafia cannot start with half of or more than half of the total number of players.')
        return
    if setup['mafia'] == 0:
        await message.channel.send('The setup is invalid. There must be at least one mafia in the game.')
        return

    # distribution of roles
    allRoles = []
    for key in setup:
        allRoles = allRoles + [key] * setup[key]
    random.shuffle(allRoles)
    for key in players:
        role = allRoles.pop()
        roles[key] = role
        user = await client.fetch_user(str(key))
        await user.send('Your role is `%s`.' % role)

    if settings['daystart']:
        game['phase'] = 1
    game['running'] = 1
    await message.channel.send('The game has begun!')


async def m_end(message):   # can only end game if currently playing (alive) or server mod/admin
    await gameEnd(message, 'None')


async def m_roles(message):
    await message.channel.send('\n'.join(roles_text))


async def m_set(message):
    if game['running']:
        await message.channel.send('Game is ongoing.')
        return
    query = message.content.split()
    if query[1] not in setup or len(query) < 3:
        await invalid(message)
        return
    try:
        num = int(query[2])
    except ValueError:
        await invalid(message)
        return
    if num != float(query[2]):
        await message.channel.send('Invalid input: inputted quantity must be integer.')
    elif num < 0:
        await message.channel.send('Invalid input: inputted quantity cannot be negative.')
    else:
        setup[query[1]] = num
        await message.channel.send('Successfully changed the number of `%ss` in the setup to `%d`.' % (query[1], num))


async def m_setup(message):
    if not sum([setup[key] for key in setup]):
        await message.channel.send('There are currently no roles in the setup. Use `m!set [role] [number]` to add some!')
        return
    await message.channel.send('\n'.join(['The setup consists of:'] + [key + ': ' + str(setup[key]) for key in setup if setup[key]]))


async def m_settings(message):
    msg = ['%s : %d - %s' % (key, settings[key], toggle_text[settings[key]][key]) for key in toggle_text[0]]
    msg += ['Time limit for %s is %s minute(s).' % (['days', 'nights'][x - 1], settings['limit' + str(x)]) for x in [1, 2]]
    await message.channel.send('\n'.join(msg))


async def m_toggle(message):
    if game['running']:
        await message.channel.send('Game is ongoing.')
        return
    query = message.content.split()
    if query[1] in settings:
        settings[query[1]] ^= 1
        await message.channel.send(toggle_text[settings[query[1]]][query[1]])
    else:
        await invalid(message)


async def m_setlimit(message):
    if game['running']:
        await message.channel.send('Game is ongoing.')
        return
    query = message.content.split()
    if query[2] == 'inf':
        settings[query[1]] = query[2]
        if query[1] == 'day':
            await message.channel.send('Time limit for day set to infinite minutes.')
        else:
            await message.channel.send('Time limit for night set to infinite minutes.')
    else:
        try:
            lim = float(query[2])
            if lim < 1:                # time limit must be at least 1 minute
                await invalid(message)
                return
            settings[query[1]] = lim
            if query[1] == 'night':
                await message.channel.send('Time limit for day set to ' + query[2] + ' minutes.')
            else:
                await message.channel.send('Time limit for night set to ' + query[2] + ' minutes.')
        except ValueError:
            await invalid(message)


async def m_join(message):
    if game['running']:
        await message.channel.send('Game is ongoing.')
        return
    if message.author.id in players:
        await message.channel.send('<@%s>, you are already in the game!' % str(message.author.id))
    else:
        players[message.author.id] = True
        roles[message.author.id] = None
        await message.channel.send('<@%s> has joined the game.' % str(message.author.id))


async def m_leave(message):
    if game['running']:
        if players[message.author.id]:
            await message.channel.send('<@%s> has elected to leave the game.' % str(message.author.id))
            players[message.author.id] = 0
            if settings['continue']:
                await death(message.author.id)
            else:
                game['running'] = 0
                await gameEnd(message, 'None')
        else:
            pass
            # player quits (leaves text and voice channels, loses role)
        return
    if message.author.id not in players:
        await message.channel.send('<@%s>, you were not in the game to begin with!' % str(message.author.id))
    else:
        players.pop(message.author.id)
        roles.pop(message.author.id)
        await message.channel.send('<@%s> has left the game.' % str(message.author.id))


async def m_vote(message):
    if not game['running']:
        await message.channel.send('The game has not yet started. Don\'t be so hasty to vote!')
        return
    if message.author.id not in players or not players[message.author.id] or not game['phase']:     # not playing, not alive, night
        await message.channel.send('You cannot vote!')
        return
    query = message.content.split()
    tar = query[1]
    try:
        if len(tar) <= 3 or tar[:2] != '<@' or tar[-1] != '>' or (int(tar[2:-1]) != client.user.id and int(tar[2:-1]) not in players) or (int(tar[2:-1]) in players and not players[int(tar[2:-1])]):
            await message.channel.send('That is an invalid voting target. Vote in the form `m!vote @user`.')
            return
    except ValueError:
        await message.channel.send('That is an invalid voting target. Vote in the form `m!vote @user`.')
        return
    await message.channel.send('<@%s> has placed their vote on <@%s>.' % (str(message.author.id), str(tar[2:-1])))
    votes[message.author.id] = int(tar[2:-1])


async def m_unvote(message):
    if not game['running']:
        await message.channel.send('The game has not yet started. There\'s nobody to unvote!')
        return
    if message.author.id not in players or not players[message.author.id] or not game['phase']:     # not playing, not alive, night
        await message.channel.send('You cannot vote!')
        return
    votes[message.author.id] = None
    await message.channel.send('<@%s> has removed their vote, and is now voting nobody.' % str(message.author.id))


async def m_status(message):
    if not game['running']:
        await message.channel.send('The game has not yet started. There are no votes in effect.')
        return
    if message.author.id not in players or not players[message.author.id] or not game['phase']:     # not playing, not alive, night
        await message.channel.send('Daytime is not in session. There are no votes in effect.')
        return
    num = sum([players[key] for key in players])
    msg = ['The votes are currently as follows:']
    count = {}
    for key in players:
        if not players[key]:
            continue
        if votes[key] == client.user.id:
            msg.append('<@%s> is currently voting for a no-lynch.' % str(key))
        elif votes[key] == None:
            msg.append('<@%s> is currently voting for nobody.' % str(key))
        else:
            msg.append('<@%s> is currently voting <@%s>' % (str(key), votes[key]))
            if votes[key] not in count:
                count[votes[key]] = 1
            else:
                count[votes[key]] += 1
    count2 = {}
    for i in range(num+1):
        count2[i] = []
    for key in count:
        count2[count[key]].append(key)
    msg.append('Voting summary:')
    for i in range(num,-1,-1):
        if count2[i]:
            msg.append(str(i) + ' vote(s) on: ' + ', '.join(['<@%s>' % str(key) for key in count2[i]]))
    msg.append('No lynch: %d vote(s)' % sum([votes[key] == client.user.id for key in votes]))
    msg.append('Nobody: %d vote(s)' % sum([votes[key] == None for key in votes]))
    await message.channel.send('\n'.join([line for line in msg]))



async def m_players(message):
    num = sum([players[key] for key in players])
    if not game['running']:
        if not num:
            await message.channel.send('There are currently no players in the game. Type `m!join` to join!')
        else:
            await message.channel.send(' '.join(['The following players are in the game:'] + ['<@%s>' % str(key) for key in players]))
        return
    await message.channel.send(' '.join(['The following players are alive:'] + ['<@%s>' % str(key) for key in players if players[key]]))


async def m_alive(message):
    if not game['running']:
        await message.channel.send('There is no ongoing game. Use `m!setup` to see the current setup of the game.')
        return
    if not settings['reveal']:
        await message.channel.send('Remaining roles are unknown, due to the `reveal` setting being toggled off.')
    else:
        await message.channel.send('\n'.join(['Remaining roles are as follows:'] + ['`%s` : %d' % (key, sum([roles[key2] == key for key2 in roles])) for key in setup]))


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
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'm!':
        return
    query = message.content[2:].split()
    if len(query) and query[0] in commands:
        func = tofunc[query[0]]
        await func(message)
    else:
        await invalid(message)





client.run('')


'''
REMEMBER TO REMOVE TOKEN WHEN COMMITTING

REMINDERS:
- message.author.id returns integer


NOTES:
- Does it require a different instance of itself per server? How does this work with DM (if a person joins in two servers). 
    - Solution: make each player only capable of joining in a single distinct server
    - Keep a map servers = {} that stores the server ID for each player...?
    - Maybe allow voting in DMs? And bot can announce vote in main chat?


GAMEPLAY:

All players are initially in both a text channel and a voice chat, and upon gamestart will be DM'd a role by the bot.

Mafia members will be in a group DM, and upon death will be removed by the bot.
Doctor and cop will receive a prompt by the bot each night phase
 - Bot will list all living players (because you can't ping people not in the DM), and will prompt input of single integer
 - Normal cop cannot investigate himself, parity cop can, doctor can save himself if selfsave = 1, mafia cannot selfkill

Daytime discussion should primarily occur in VC, but players can use text channels if they want. Text channel will be used for voting and other in-game commands.



Nighttime will occur in DMs. The main text channel will be locked and nobody will be able to speak there (might need to end game? rethink this).
Graveyard text channel will be able to continue to talk.


'''
