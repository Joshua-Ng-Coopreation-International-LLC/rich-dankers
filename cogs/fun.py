from nextcord.ext import commands
from utils.embed import embed
from humanfriendly import parse_timespan
import nextcord, datetime
from utils.perms import funcog_permission_handler


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandNotFound):
            return
        if ctx.cog != self:
            return
        await ctx.send(
            f"An error has occurred [{self.__class__.__name__} COG].\n```{exception}```"
        )

    @commands.command()
    @funcog_permission_handler(command="bon")
    async def bon(self, ctx, target: nextcord.Member = None):
        responded = False
        await ctx.message.delete()
        if target:
            await ctx.send(
                f"**{target.name}** has been **banned** from **{ctx.guild.name}** permanently."
            )
            responded = True
        if not responded:
            await ctx.send(
                f"""```{self.bot.command_prefix}ban <member> [reason]
     ^^^^^^^^
member is a required argument that is missing.```""",
                delete_after=8,
            )

    @commands.command()
    @funcog_permission_handler(command="moot")
    async def moot(self, ctx, target: nextcord.Member = None, duration: str = None):
        responded = False
        await ctx.message.delete()
        if target and duration:
            time_delta = datetime.timedelta(seconds=parse_timespan(duration))
            expiry_time = datetime.datetime.now() + time_delta
            await ctx.send(
                f"**{target.name}** has been **muted** in **{ctx.guild.name}** for {nextcord.utils.format_dt(expiry_time, 'R')}"
            )
            responded = True
        if not responded:
            await ctx.send(
                f"""{self.bot.command_prefix}moot <member> <duration>
 ^^^^^^^^
member is a required argument that is missing.""",
                delete_after=8,
            )

    @commands.command()
    @funcog_permission_handler(command="exit")
    async def exit(self, ctx):
        await ctx.message.delete()
        await ctx.send(
            f"<a:pepe_exit:1280251861944762418> | {ctx.author.mention} has left the chat."
        )

    @commands.command()
    @funcog_permission_handler(command="enter")
    async def enter(self, ctx):
        await ctx.message.delete()
        await ctx.send(
            f"<a:pepe_enter:1280252298915741717> | {ctx.author.mention} has entered the chat."
        )


def setup(bot):
    bot.add_cog(Fun(bot))
