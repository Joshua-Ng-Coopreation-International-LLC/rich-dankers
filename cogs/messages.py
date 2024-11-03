import json, nextcord, cooldowns, datetime
from utils.embed import embed
from nextcord.ext import commands
from nextcord import SlashOption
from cooldowns import CallableOnCooldown


class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandNotFound):
            return
        if ctx.cog != self:
            return
        await ctx.send(
            f"An error has occurred [{self.__class__.__name__} COG].\n{exception}"
        )

    @commands.Cog.listener()
    async def on_application_command_error(
        self, interaction: nextcord.Interaction, error
    ):
        error = getattr(error, "original", error)

        if isinstance(error, CallableOnCooldown):
            await interaction.send(
                f"You are being rate-limited! Retry in `{error.retry_after:.2f}` seconds."
            )
        else:
            raise error

    @commands.group()
    async def goal(self, ctx):
        if ctx.invoked_subcommand:
            return
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        if len(ctx.guild.humans) >= config["membergoal"]:
            await ctx.reply(
                embed=embed(
                    "Member Goal <a:animated_tada1:1279873193330343936>",
                    description=f"- We have reached our goal of {config['membergoal']} humans in the server!\n- Thank you for the {len(ctx.guild.humans)} humans in our server!",
                )
            )
        else:
            await ctx.reply(
                embed=embed(
                    "Member Goal <a:animated_tada1:1279873193330343936>",
                    description=f"- Help us reach {config['membergoal']} humans in the server!\n- We are currently at {len(ctx.guild.humans)} humans, just {config['membergoal']-len(ctx.guild.humans)} to go!",
                )
            )

    @goal.command()
    @commands.has_any_role(1274079697684402237, 1280220951077720178)
    async def set(self, ctx, goal: int):
        try:
            with open("config.json") as config_file:
                config = json.load(config_file)
            config["membergoal"] = goal
            with open("config.json", "w") as file:
                json.dump(config, file, indent=4)
        except:
            await ctx.reply("An error had occurred.")
            return
        await ctx.reply(f"Member Goal changed successfully to {goal}")

    @commands.command()
    @commands.has_any_role(1276204026857390141, 1280220951077720178)
    async def payout(self, ctx, target: nextcord.Member, *, prize: str):
        view = nextcord.ui.View()
        view.add_item(
            nextcord.ui.Button(
                label="Click here to jump to tickets",
                style=nextcord.ButtonStyle.link,
                url="https://discord.com/channels/1274056217010114600/1275509807050395769",
                emoji="<a:Unreal_Richi_Rich:1285302918387470496>",
            )
        )
        await ctx.message.delete()
        await ctx.send(
            content=target.mention,
            embed=embed(
                "Payout Notification <a:money1:1280477464442830911>",
                description=f"Please head to <#1275509807050395769> to claim your **{prize}** __with{nextcord.utils.format_dt(datetime.datetime.now()+datetime.timedelta(hours=24), "R")}__.\nMake sure to copy the message link to make this process faster.\nThank you very much!",
                footer=f"Sent by {ctx.author.name} ({ctx.author.id}) - {datetime.datetime.now()}",
            ),
            view=view,
        )

    @nextcord.slash_command(name="ping")
    @commands.has_any_role(1277204324920983572, 1280220951077720178)
    async def ping(self, interaction):
        return

    @ping.subcommand(name="giveaway")
    @commands.has_any_role(1277204324920983572, 1280220951077720178)
    async def giveawayping(
        self,
        interaction,
        type: int = SlashOption(
            name="type",
            description="What type of giveaway are you hosting?",
            choices={
                "mega": 1,
                "mini": 2,
            },
        ),
        prize: str = SlashOption(
            name="prize", description="What is the prize of the giveaway?"
        ),
        donator: str = SlashOption(
            name="donator",
            description="send the link to the donation here if you funded it yourself leave it blank",
            required=False,
        ),
        notes: str = SlashOption(
            name="notes",
            description="Any notes you want to add?",
            required=False,
        ),
    ):
        dict = {1: 1274065965402820781, 2: 1296512312202494093}
        type = dict[type]
        view = nextcord.ui.View()
        role = interaction.guild.get_role(type)
        msg = await interaction.response.send_message(
            content=f"{role.mention}",
            embed=embed(
                title="Giveaway <a:giveaway:1297975613339992064>",
                description=f"{interaction.user.mention} just hosted a giveaway(s)!\nPlease create a ticket to claim your prize(s)!)",
            ),
            allowed_mentions=nextcord.AllowedMentions.all(),
        )
        msg = await msg.fetch()
        view.add_item(
            nextcord.ui.Button(
                label="Jump the giveaway",
                style=nextcord.ButtonStyle.link,
                url=f"{msg.jump_url}",
                emoji="<a:pin:1297983351688532028>",
            )
        )
        loggingchannel = interaction.guild.get_channel(1279349251821932604)
        await loggingchannel.send(
            embed=embed(
                title=f"New Giveaway Log by {interaction.user.name} ({interaction.user.id})",
                description=f"**Type:**  {type}\n**Prize:** {prize}\n**Sponsor link:** {donator}\n**Giveaway link:** {msg.jump_url}\n**Notes:** {notes}\n**User:** {interaction.user.mention} ({interaction.user.id})",
            ),
            view=view,
        )


def setup(bot):
    bot.add_cog(Messages(bot))
