# CLANG
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/maidnaut/clang?style=for-the-badge)

Clang is an all-in-one self hosted discord bot witten with pycord, inspired by Valkyrja. Handles moderation, tickets, logging, notes, and fun commands.

Clang is fully modular, extendable, extensible, and customizable with its functionality to dynamically load plugins.

Clang is a skull kept alive by eldritch magic. It screams and talks nonsense.

Clang.

<img src="Clang.png" width=100px> 
</div>

<br>

## Dependencies
- py-cord
- rich
- alt-profanity-check
- audioop-lts

<br>

## Package build Clang (easy)
1) Git clone the pkgbuild version (made by Jorgen): `https://github.com/Jorgen10/clang-pkgbuild.git`
2) cd into Clang's directory: `cd clang-pkgbuild`
3) Run makepkg: `makepkg -si`
4) Modify `/opt/python-clang/.env` to add your bot token
5) Run Clang:
    - To run it as a systemd service, use `sudo systemctl enable --now python-clang`
    - Alternatively, you can manually run `cd /opt/python-clang && sudo -u python-clang ./venv/bin/python ./clang.py`

## Manual install
1) Create a venv in Clang's directory: `python3 -m venv ~/path_to_clang/.venv`
2) Set the venv source: `source ~/path_to_clang/.venv/bin/activate`
3) Install py-cord and Clang's dependencies: `pip install py-cord rich alt-profanity-check audioop-lts`
4) cd into Clang's directory and run it: `python3 clang.py`

If you want, you can alias Clang to something in `.bashrc` so you don't have to initialize the venv manually every time,

```sh
alias clang="cd ~/clang && source .venv/bin/activate && python clang.py"
```

<br>

## Post-install
Once you have Clang set up on your host machine/server, there's a few things you need to do to get it up and running.

### Phase 1
1) Go to [discord's developer portal](https://discord.com/developers/) and create a new bot for your instance of Clang.
2) In the bot tab and generate a new token. Hold onto it because we're going to need it in a second.
3) Generate a new invite link for Clang in the OAuth tab, selecting `bot` in the scopes.
4) If you're running Clang yourself, it'll ask you to paste the token into the terminal. If you installed it with the makepkg option, skip this step because you should have already made the .env file for the token yourself.

### Phase 2
After you've got Clang connected to your server, you need to create the required roles and channels for its base moderation roles. By default Clang should accept (most) commands from the server owner, but to use the moderation suite you need to create the following roles and channels. If you'd like to skip !op roles, just run `!elevation off`, and if you want do disable the submod role, you can just choose to not set it.

All channels and roles **MUST** be supplied by their id.

Roles (run with `!setrole <name> <id>`):
- Jailed
- Submod
- Mod
- Op
- Admin
- Root

Channels (run with `!setchannel <name> <id>`):
- joinlog
- modlog
- logs
- ticketlog
- jaillog
- mod_channel

Categories (run with `!setchannel <name> <id>`):
- ticket_category
- jail_category
- mod_category

After that, Clang should be good to go!

<br>

## Commands

| Command                       | Description                                                 |
|------------------------------|--------------------------------------------------------------|
| `!cookies`                   | Shows your cookies and supplies commands                     |
| `!nom`                       | Eats a cookie                                                |
| `!give <user>`               | Gives the mentioned user one of your cookies                 |
| `!transfer <user> (amount)`  | Cookie credit transfer                                       |
| `!leaderboard`               | Shows the cookie leaderboard                                 |
| `!gamble`                    | (Alias: !bet) Gamble your cookies for a chance to win more   |
| `!clang`                     | Make Clang say stuff                                         |
| `!fortune`                   | Get a fortune from Clang                                     |
| `!flip`                      | Flip a coin (heads or tails)                                 |
| `!roll <#d#>`                | Roll x number of dice with x sides (e.g. 2d6)                |
| `!8ball <question>`          | Ask Clang a question!                                        |
| `!xkcd <id>`                 | Shows a comic from xkcd                                      |
| `!setping on, off`           | Enables or disables ping responses from Clang                |
| `!whois <user:optional>`     | Displays user data                                           |
| `!ping`                      | Check Clang's latency                                        |
| `!avatar <user:optional>`    | Displays an avatar                                           |
| `!serverinfo`                | Displays server data                                         |
| `!source`                    | Github url                                                   |
| `!aw`                        | Searches the Arch Wiki                                       |
| `!gw <query>`                | Searches the Gentoo Wiki                                     |
| `!proton <query>`            | Searches the ProtonDB                                        |
