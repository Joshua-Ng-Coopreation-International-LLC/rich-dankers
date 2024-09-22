import nextcord, json, traceback, os, sys
from nextcord.ext import commands
from utils.embed import embed

token = None
guilds = None
cogdir = None


def config():
    global token, guilds, cogdir
    with open("config.json") as config_file:
        config = json.load(config_file)

    token = config["token"]
    guilds = config["guilds"]
    cogdir = config["cogdir"]


config()
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="t", intents=intents)


@bot.event
async def on_ready():
    print("Connected.")
    await bot.sync_all_application_commands()
    print("Synced all slash commands [/]")
    for filename in os.listdir(cogdir):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:

                bot.load_extension(cog_name)
                print(f"Loaded {cog_name} successfully.")
            except Exception as e:
                print(f"Failed to load {cog_name}: {e}")


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
    print(commands.Command.has_error_handler(ctx))
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


@bot.command(name="load")
@commands.is_owner()
async def load_cog(ctx, cog: str):
    try:
        bot.load_extension(f"cogs.{cog}")
        await ctx.reply(embed=embed("Load", f"Successfully loaded `{cog}` cog."))
    except Exception as e:
        await ctx.reply(
            embed=embed("Load", f"Failed to load `{cog}` cog.\nError: {str(e)}")
        )


@bot.command(name="unload")
@commands.is_owner()
async def unload_cog(ctx, cog: str):
    try:
        bot.unload_extension(f"cogs.{cog}")
        await ctx.reply(embed=embed("Unload", f"Successfully unloaded `{cog}` cog."))
    except Exception as e:
        await ctx.reply(
            embed=embed("Unload", f"Failed to unload `{cog}` cog.\nError: {str(e)}")
        )


@bot.command(name="reload")
@commands.is_owner()
async def reload_cog(ctx, cog: str):
    try:
        bot.reload_extension(f"cogs.{cog}")
        await ctx.reply(embed=embed("Reload", f"Successfully reloaded `{cog}` cog."))
    except Exception as e:
        await ctx.reply(
            embed=embed("Reload", f"Failed to reload `{cog}` cog.\nError: {str(e)}")
        )


@bot.command(name="load_all")
@commands.is_owner()
async def load_all_cogs(ctx):
    cogs = []
    for filename in os.listdir(cogdir):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            cogs.append(cog_name)

    success = []
    failure = []
    for cog in cogs:
        try:
            bot.load_extension(f"cogs.{cog}")
            success.append(cog)
        except Exception as e:
            failure.append(f"{cog}: {str(e)}")
    await ctx.reply(
        embed=embed(
            "Load All",
            f"Successfully loaded: {', '.join(success)}\nFailed to load: {', '.join(failure)}",
        )
    )


@bot.command(name="unload_all")
@commands.is_owner()
async def unload_all_cogs(ctx):
    cogs = []
    for filename in os.listdir(cogdir):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            cogs.append(cog_name)
    success = []
    failure = []
    for cog in cogs:
        try:
            bot.unload_extension(f"cogs.{cog}")
            success.append(cog)
        except Exception as e:
            failure.append(f"{cog}: {str(e)}")
    await ctx.reply(
        embed=embed(
            "Unload All",
            f"Successfully unloaded: {', '.join(success)}\nFailed to unload: {', '.join(failure)}",
        )
    )


@bot.command(name="reload_all")
@commands.is_owner()
async def reload_all_cogs(ctx):
    cogs = []
    for filename in os.listdir(cogdir):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            cogs.append(cog_name)
    success = []
    failure = []
    for cog in cogs:
        try:
            bot.reload_extension(f"cogs.{cog}")
            success.append(cog)
        except Exception as e:
            failure.append(f"{cog}: {str(e)}")
    await ctx.reply(
        embed=embed(
            "Reload All",
            f"Successfully reloaded: {', '.join(success)}\nFailed to reload: {', '.join(failure)}",
        )
    )


@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    try:
        await bot.sync_all_application_commands()
    except Exception as e:
        await ctx.reply(str(e))
        return
    await ctx.send("Synced commands.")


@bot.command(name="restart")
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Starting restart process.")
    python = sys.executable
    os.execl(python, python, *sys.argv)


@bot.command(name="hi")
async def hi(ctx, jaospfad: str):
    return


bot.run(token)
