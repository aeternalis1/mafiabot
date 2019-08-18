# mafiabot
Discord bot for mafia, implemented in python using discord.py

This bot enables users to set up and play a game of mafia via text, voice, and direct messaging channels on Discord.


## Bot commands

### Basic

`m!help` displays the help screen, with a list of commands.

`m!h2p` describes how to play: the basic rules and premise of the game.

`m!start` begins a new round of mafia.

`m!end` ends the current game, if existing. Can only be called by a moderator or a player.

### Setup

`m!roles` lists all available roles that can be added to the game.

`m!set [role] [number]` sets the quantity of `[role]` in the setup to `[number]`. e.g. `m!set villager 3`

`m!setup` shows the full complement of roles in the current setup.

`m!settings` displays all the settings of the current game.

`m!toggle [setting]` flips `[setting]` from on to off, or vice versa. Type `m!settings` to see options. e.g. `m!toggle daystart`

`m!setlimit [phase] [time]` sets the time limit for `[phase]` to `[time]` in minutes. `[time]` can be a positive real number at least 1 or `inf`. e.g. `m!setlimit day 10`

`m!join` adds you to the game.

`m!leave` removes you from the game. This may end an ongoing game, so be careful using this command.

### In-game

`m!vote [player]` puts your current vote on `player`. Vote this bot to set your vote to no-lynch. e.g. `m!vote @mafiabot`

`m!unvote` sets your vote to nobody (no vote).

`m!status` displays all players and their votes, as well as the vote count on each player.

`m!players` displays all players who are currently alive

`m!alive` displays all the roles and their quantities that are still in play.

`m!dead` displays the players in the graveyard and their roles (if roles are revealed upon death).

`m!time` displays the amount of time left, before the day or night ends.

## Roles and settings

### Roles

`villager`: Village-aligned role. No special powers.

`normalcop`: Village-aligned role, capable of determining the alignment of a target player during nighttime.

`paritycop`: Village-aligned role, capable of determining whether his LAST TWO targets are of the same alignment (will not get a report after night 1).

`doctor`: Village-aligned role, capable of saving a target player from death during nighttime.

`mafia`: Mafia-aligned role. Capable of killing a villager during nighttime with fellow mafia.

### Game settings

`daystart`: If toggled, the game begins during a day phase in lieu of a night phase.

`selfsave`: If toggled, doctors are allowed to save themselves.

`conssave`: If toggled, doctors may save the same target on consecutive days.

`continue`: If toggled, the game will continue even if a living player leaves.

`reveal`: If toggled, players' roles will be revealed upon death.

`limit1`: Determines the time limit for day phases (by default infinite).

`limit2`: Determines the time limit for night phases (by default infinite).