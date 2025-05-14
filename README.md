# CLANG

Clang is an all-in-one self hosted discord bot witten with pycord, inspired by Valkyrja. Handles moderation, tickets, logging, notes, and fun commands.

Clang is fully modular, extendable, extensible, and customizable with its functionality to dynamically load plugins.

Clang is a skull kept alive by eldritch magic. It screams and talks nonsense.

Clang also comes with its own custom mock shell built in for external configuration and management.

Clang.

![image](https://i.imgur.com/UbjUrys.png)

---

To run Clang, first do the following:

1) Create a venv in Clang's directory. "python3 -m venv ~/path_to_clang/.venv"
2) Set the venv source: "source ~/path_to_clang/.venv/bin/activate"
3) Install py-cord & rich: "pip install py-cord rich"
4) cd into Clang's directory and run it: "python3 clang.py"

If you want, you can alias Clang to something in .bashrc so you don't have to initialize the venv manually every time,
alias clang="cd ~/clang && source .venv/bin/activate && python clang.py"
