from nextcord.ext import commands
import json


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def premium_command_handler(command: str = True):
    if command == True:

        async def predicate(ctx):
            list = (
                load_config()["premiumcommands"]["default"]
                + load_config()["premiumcommands"]["bypassall"]
            )
            return commands.has_any_role(*list)

    else:
        if command in load_config()["premiumcommands"]:

            async def predicate(ctx):
                list = (
                    load_config()["premiumcommands"][command]
                    + load_config()["premiumcommands"]["bypassall"]
                )
                return commands.has_any_role(*list)

        else:

            async def predicate(ctx):
                list = (
                    load_config()["premiumcommands"]["default"]
                    + load_config()["premiumcommands"]["bypassall"]
                )
                return commands.has_any_role(*list)

    return commands.check(predicate)


def ping_group_command_handler(command: str = True):
    if command == True:

        async def predicate(ctx):
            list = (
                load_config()["grouppingcommands"]["default"]
                + load_config()["grouppingcommands"]["bypassall"]
            )
            return commands.has_any_role(*list)
