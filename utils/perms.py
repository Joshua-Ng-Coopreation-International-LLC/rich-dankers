from nextcord.ext import commands, application_checks
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


def staff_role_converter(role_name: str):
    try:
        return (
            load_config()["roles"]["staffroles"][role_name]
            if role_name in load_config()["roles"]["staffroles"]
            else load_config()["masterrole"]
        )
    except KeyError:
        return load_config()["staffroles"]["botdeveloper"]


def ping_group_slash_permission_handler(value: str):
    config = load_config()
    ping_config = config["ping"]
    roles_to_check = ping_config.get(value, [])
    bypass_roles = ping_config.get("bypassall", [])
    role_ids = []
    for role in roles_to_check + bypass_roles:
        if isinstance(role, str):
            role_ids.extend(staff_role_converter(role))
        else:
            role_ids.append(role)

    async def predicate(interaction):
        user_roles = [role.id for role in interaction.user.roles]
        return application_checks.has_any_role(
            *(role_id in user_roles for role_id in role_ids)
        )

    return application_checks.check(predicate)
