from nextcord.ext import commands
import json


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def funcog_permission_handler(command: str):
    if not command in ["bon", "moot", "enter", "exit"]:

        async def predicate(ctx):
            list = load_config()["funcog"]["default"]
            return commands.has_any_role(*list)

    else:

        async def predicate(ctx):
            list = load_config()["funcog"][command]
            return commands.has_any_role(*list)

    return commands.check(predicate)
