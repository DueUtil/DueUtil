import discord

import generalconfig as gconf
from .. import util, commands
from ..permissions import Permission

class FeedbackHandler:
    """
    Another weird class to make something easier.
    """

    def __init__(self, **options):
        self.channel = options.get('channel')
        self.type = options.get('type').lower()
        self.trello_list = options.get('trello_list')

    async def send_report(self, ctx, message):
        author = ctx.author
        author_name = "%s#%s" % (author.name, str(author.discriminator))

        trello_link = await util.trello_client.add_card(board_url=gconf.trello_board,
                                                        name=message,
                                                        desc=("Automated %s added by DueUtil\n" % self.type
                                                              + "Author: %s (id %s)" % (author_name, author.id)),
                                                        list_name=self.trello_list,
                                                        labels=["automated"])
        author_icon_url = author.avatar_url
        if author_icon_url == "":
            author_icon_url = author.default_avatar_url
        report = discord.Embed(color=gconf.EMBED_COLOUR)
        report.set_author(name=author_name, icon_url=author_icon_url)
        report.add_field(name=self.type.title(), value="%s\n\n[Trello card](%s)" % (message, trello_link), inline=False)
        report.add_field(name=ctx.server.name, value=ctx.server.id)
        report.add_field(name=ctx.channel.name, value=ctx.channel.id)
        report.set_footer(text="Sent at " + util.pretty_time())
        await util.say(ctx.channel,
                       ":mailbox_with_mail: Sent! You can view your %s here: <%s>" % (self.type, trello_link))
        await util.say(self.channel, embed=report)


bug_reporter = FeedbackHandler(channel=gconf.bug_channel, type="bug report", trello_list="bug reports")
suggestion_sender = FeedbackHandler(channel=gconf.feedback_channel, type="suggestion", trello_list="suggestions")


@commands.command(permission=Permission.DISCORD_USER, args_pattern="S")
@commands.ratelimit(cooldown=300, error=":cold_sweat: Please don't submit anymore reports for a few minutes!")
async def bugreport(ctx, report, **_):
    """
    [CMD_KEY]bugreport (report)
    
    Leaves a bug report on the official DueUtil server and trello.
    
    """

    await bug_reporter.send_report(ctx, report)


@commands.command(permission=Permission.DISCORD_USER, args_pattern="S")
@commands.ratelimit(cooldown=300, error=":hushed: Please no more suggestions (for a few minutes)!")
async def suggest(ctx, suggestion, **_):
    """
    [CMD_KEY]suggest (suggestion)
    
    Leaves a suggestion on the official server and trello.
    
    """

    await suggestion_sender.send_report(ctx, suggestion)
