import nextcord, json, traceback, os, sys, typing
from nextcord.ext import commands, tasks
from utils.embed import embed
from utils.load import load_config

token = None
guilds = None
cogdir = None


def config():
    global token, guilds, cogdir
    with open("config.json") as config_file:
        config = json.load(config_file)
    if not config["setupcomplete?"]:
        print(
            "Please setup the config.json file properly before changing setupcomplete? to true."
        )
        sys.exit()
    if not any(key in config for key in ["token", "guilds", "cogdir"]):
        print("Please setup the config.json file properly.")
        sys.exit()
    token = config["token"]
    guilds = config["guilds"]
    cogdir = config["cogdir"]


class HelpCommand(commands.MinimalHelpCommand):
    def get_command_signature(self, command):
        return (
            f"{self.context.clean_prefix}{command.qualified_name} {command.signature}"
        )

    async def _help_embed(
        self,
        title: str,
        description: typing.Optional[str] = None,
        mapping: typing.Optional[str] = None,
        command_set: typing.Optional[typing.Set[commands.Command]] = None,
        set_author: bool = False,
    ) -> nextcord.Embed:
        embed = nextcord.Embed(title=title)

        if description:
            embed.description = description
        else:
            embed.description = f"Welcome to {self.context.bot.user.name}'s help menu!"

        if set_author:
            avatar = (
                self.context.bot.user.avatar or self.context.bot.user.default_avatar
            )
            embed.set_author(name=self.context.bot.user.name, icon_url=avatar.url)

        if command_set:
            # show help about all commands in the set
            filtered = await self.filter_commands(command_set, sort=True)
            for command in filtered:
                signature = self.get_command_signature(command)
                arg_info = []
                for param in command.clean_params.values():
                    param_type = (
                        param.annotation.__name__
                        if param.annotation != param.empty
                        else "Optional"
                    )
                    arg_info.append(f"`{param.name}`: `{param_type}`")
                arg_info_formatted = "\n".join(arg_info)
                value = "No help provided"
                # command_docs.get(
                #    f"{command.cog_name} {command.qualified_name}", "No help provided."
                # )
                embed.add_field(
                    name=signature,
                    value=f"\n{arg_info_formatted}" if arg_info else value,
                    inline=False,
                )
        elif mapping:
            embed.description = f"{embed.description}\nHello, this is bot is designed for dank based server, to order one please feel free to contact `joshuang.site` @ Discord or me@msft.joshuang.site via Email."
            # add a short description of commands in each cog
            for cog, command_set in mapping.items():
                filtered = await self.filter_commands(command_set, sort=True)
                if not filtered:
                    continue
                name = cog.qualified_name if cog else "No category"
                emoji = getattr(cog, "COG_EMOJI", None)
                cog_label = f"{emoji} {name}" if emoji else name
                cmd_list = "\u2002".join(
                    f"`{self.context.clean_prefix}{cmd.name}`" for cmd in filtered
                )
                value = (
                    f"{cog.description}\n{cmd_list}"
                    if cog and cog.description
                    else cmd_list
                )
                embed.add_field(name=cog_label, value=value)

        return embed

    async def send_bot_help(self, mapping: dict):
        embed = await self._help_embed(
            title="Help Menu",
            description=None,
            mapping=mapping,
            set_author=False,
        )
        self.response = await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        arg_info = []
        for param in command.clean_params.values():
            param_type = (
                param.annotation.__name__
                if param.annotation != param.empty
                else "Optional"
            )
            arg_info.append(f"`{param.name}`: `{param_type}`")
        arg_str = "\n".join(arg_info)
        embed = await self._help_embed(
            title=f"{command.qualified_name}",
            description=(
                f"{command.help}\n\nArguments: \n{arg_str}"
                if command.help
                else f"No description provided.\n\nArguments:\n{arg_str}"
            ),
            command_set=(
                command.commands if isinstance(command, commands.Group) else None
            ),
        )
        await self.get_destination().send(embed=embed)


config()

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="r", intents=intents)
bot.help_command = HelpCommand()


@bot.event
async def on_ready():
    print("Connected.")
    for filename in os.listdir(cogdir):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:

                bot.load_extension(cog_name)
                print(f"Loaded {cog_name} successfully.")
            except Exception as e:
                print(f"Failed to load {cog_name}: {e}")
    try:
        await bot.sync_all_application_commands()
    except Exception as e:
        print(f"Failed to sync all slash commands: {e}")
        return
    print("Synced all slash commands [/]")


@bot.event
async def on_guild_join(guild):
    if guild.id in guilds:
        return
    try:
        await guild.owner.send(
            "I'm afraid I'm not allowed to join guilds.\n"
            "This is a custom made bot. If you would like to order one, "
            "please contact `joshuang.site` <@1043592531855822848>. OR email me@msft.joshuang.site."
        )
    except nextcord.Forbidden:
        print("Couldn't send a message to the guild owner.")

    for channel in guild.text_channels:
        try:
            await channel.send(
                "I'm afraid I'm not allowed to join guilds.\n"
                "This is a custom made bot. If you would like to order one, "
                "please contact `joshuang.site` <@1043592531855822848>. OR email me@msft.joshuang.site."
            )
            break
        except nextcord.Forbidden:
            continue

    await guild.leave()


@bot.event
async def on_command_error(ctx, exception):
    if commands.Command.has_error_handler(ctx):
        return
    if isinstance(exception, commands.errors.CommandNotFound):
        return
    if ctx.cog:
        return
    await ctx.send(f"An error has occurred.\n```{exception}```")


@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! {latency}ms")


@bot.command(name="refreshconfig")
@commands.is_owner()
async def refreshconfig(ctx):
    config()
    await ctx.send("Config refreshed successfully.")


@bot.command(name="eval")
@commands.is_owner()
async def eval_fn(ctx, *, code):
    language_specifiers = [
        "python",
        "py",
        "javascript",
        "js",
        "html",
        "css",
        "php",
        "md",
        "markdown",
        "go",
        "golang",
        "c",
        "c++",
        "cpp",
        "c#",
        "cs",
        "csharp",
        "java",
        "ruby",
        "rb",
        "coffee-script",
        "coffeescript",
        "coffee",
        "bash",
        "shell",
        "sh",
        "json",
        "http",
        "pascal",
        "perl",
        "rust",
        "sql",
        "swift",
        "vim",
        "xml",
        "yaml",
    ]
    loops = 0
    while code.startswith("`"):
        code = "".join(list(code)[1:])
        loops += 1
        if loops == 3:
            loops = 0
            break
    for language_specifier in language_specifiers:
        if code.startswith(language_specifier):
            code = code.lstrip(language_specifier)
    while code.endswith("`"):
        code = "".join(list(code)[0:-1])
        loops += 1
        if loops == 3:
            break
    code = "\n".join(f"    {i}" for i in code.splitlines())
    code = f"async def eval_expr():\n{code}"

    def send(
        text,
    ):
        bot.loop.create_task(ctx.send(text))

    env = {
        "bot": bot,
        "client": bot,
        "ctx": ctx,
        "print": send,
        "_author": ctx.author,
        "_message": ctx.message,
        "_channel": ctx.channel,
        "_guild": ctx.guild,
        "_me": ctx.me,
    }
    env.update(globals())
    try:
        exec(code, env)
        eval_expr = env["eval_expr"]
        result = await eval_expr()
        if result:
            await ctx.send(result)
    except:
        await ctx.send(f"{traceback.format_exc()}")


def is_owner(ctx):
    return ctx.author.id == bot.owner_id


def manage_cog(bot, operation, cog_name):
    operation_map = {
        "load": bot.load_extension,
        "unload": bot.unload_extension,
        "reload": bot.reload_extension,
    }
    try:
        operation_map[operation](f"cogs.{cog_name}")
        return embed(
            operation.capitalize(), f"Successfully {operation}ed `{cog_name}` cog."
        )
    except Exception as e:
        return embed(
            operation.capitalize(),
            f"Failed to {operation} `{cog_name}` cog.\nError: {str(e)}",
        )


def manage_all_cogs(bot, operation):
    operation_map = {
        "load": bot.load_extension,
        "unload": bot.unload_extension,
        "reload": bot.reload_extension,
    }
    cogs = [
        filename[:-3] for filename in os.listdir(cogdir) if filename.endswith(".py")
    ]
    success = []
    failure = []
    for cog in cogs:
        try:
            operation_map[operation](f"cogs.{cog}")
            success.append(cog)
        except Exception as e:
            failure.append(f"{cog}: {str(e)}")
    return embed(
        f"{operation.capitalize()} All",
        f"Successfully {operation}ed: {', '.join(success)}\nFailed to {operation}: {', '.join(failure)}",
    )


@bot.command(name="load")
@commands.is_owner()
async def load_cog(ctx, cog: str):
    await ctx.reply(embed=manage_cog(bot, "load", cog))


@bot.command(name="unload")
@commands.is_owner()
async def unload_cog(ctx, cog: str):
    await ctx.reply(embed=manage_cog(bot, "unload", cog))


@bot.command(name="reload")
@commands.is_owner()
async def reload_cog(ctx, cog: str):
    await ctx.reply(embed=manage_cog(bot, "reload", cog))


@bot.command(name="load_all")
@commands.is_owner()
async def load_all_cogs(ctx):
    await ctx.reply(embed=manage_all_cogs(bot, "load"))


@bot.command(name="unload_all")
@commands.is_owner()
async def unload_all_cogs(ctx):
    await ctx.reply(embed=manage_all_cogs(bot, "unload"))


@bot.command(name="reload_all")
@commands.is_owner()
async def reload_all_cogs(ctx):
    await ctx.reply(embed=manage_all_cogs(bot, "reload"))


@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    try:
        await bot.sync_all_application_commands()
    except Exception as e:
        await ctx.reply(str(e))
        return
    await ctx.send("Synced commands.")


@tasks.loop(hours=1)
async def resync_commands():
    try:
        await bot.sync_all_application_commands()
    except Exception as e:
        print(f"Failed to sync commands: {str(e)}")
        return
    print("[/] Synced commands successfully.")


@bot.command(name="restart")
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Starting restart process.")
    python = sys.executable
    os.execl(python, python, *sys.argv)


bot.run(token)
