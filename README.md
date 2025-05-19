<div align=center> 
<img src="Clang.png" width=100px>


# CLANG
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/maidnaut/clang?style=for-the-badge)



Note: As of 0.4b, profanity_check is a required import.

Clang is an all-in-one self hosted discord bot witten with pycord, inspired by Valkyrja. Handles moderation, tickets, logging, notes, and fun commands.

Clang is fully modular, extendable, extensible, and customizable with its functionality to dynamically load plugins.

Clang is a skull kept alive by eldritch magic. It screams and talks nonsense.

Clang also comes with its own custom mock shell built in for external configuration and management.

Clang.

<img src="ClangMessage.png">
<hr>
</div>

## Commands

| Command                       | Description                                                 |
|------------------------------|--------------------------------------------------------------|
| `!cookies`                   | Shows your cookies and supplies commands                     |
| `!nom`                       | Eats a cookie                                                |
| `!give <user>`               | Gives the mentioned user one of your cookies                 |
| `!transfer <user> (amount)`  | Cookie credit transfer                                       |
| `!leaderboard`               | Shows the cookie leaderboard                                 |
| `!clang`                     | Make Clang say stuff                                         |
| `!fortune`                   | Get a fortune from Clang                                     |
| `!flip`                      | Flip a coin (heads or tails)                                 |
| `!roll <#d#>`                | Roll x number of dice with x sides (e.g. 2d6)                |
| `!8ball <question>`          | Ask Clang a question!                                        |
| `!xkcd <id>`                 | Shows a comic from xkcd                                      |
| `!whois <user:optional>`     | Displays user data                                           |
| `!ping`                      | Check Clang's latency                                        |
| `!avatar <user:optional>`    | Displays an avatar                                           |
| `!serverinfo`                | Displays server data                                         |
| `!aw`                        | Searches the Arch Wiki                                       |
| `!gw <query>`                | Searches the Gentoo Wiki                                     |
| `!proton <query>`            | Searches the ProtonDB                                        |



# Running Clang Locally
To run Clang, first do the following:

1) Create a venv in Clang's directory: `python3 -m venv ~/path_to_clang/.venv`
2) Set the venv source: `source ~/path_to_clang/.venv/bin/activate`
3) Install py-cord, rich and profanity_check: `pip install py-cord rich profanity_check`
4) cd into Clang's directory and run it: `python3 clang.py`

If you want, you can alias Clang to something in `.bashrc` so you don't have to initialize the venv manually every time,

```sh
alias clang="cd ~/clang && source .venv/bin/activate && python clang.py"
```
