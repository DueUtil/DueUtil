import json
import os
import re
import subprocess

import discord

import dueutil.permissions
import generalconfig as gconf
from dueutil.game.helpers import imagehelper
from dueutil.permissions import Permission
from .. import commands, util, events


# Import all game things. This is (bad) but is needed to fully use the eval command


@commands.command(args_pattern=None)
async def permissions(ctx, *args, **details):
    """
    [CMD_KEY]permissions
    
    A check command for the permissions system.
    
    """

    permissions_report = ""
    for permission in dueutil.permissions.permissions:
        permissions_report += ("``" + permission.value[1] + "`` → "
                               + (":white_check_mark:" if dueutil.permissions.has_permission(ctx.author,
                                                                                             permission)
                                  else ":no_entry:") + "\n")
    await util.say(ctx.channel, permissions_report)


@commands.command(args_pattern="IIIS", hidden=True)
async def test(ctx, *args, **details):
    """A test command"""

    # print(args[0].__dict__)
    # args[0].save()
    # await imagehelper.test(ctx.channel)
    await util.say(ctx.channel, ("Yo!!! What up dis be my test command fo show.\n"
                                 "I got deedz args ```" + str(args) + "```!"))


@commands.command(args_pattern="RR", hidden=True)
async def add(ctx, *args, **details):
    """
    [CMD_KEY]add (number) (number)
    
    One of the first test commands for Due2
    I keep it for sentimental reasons
    
    """

    first_number = args[0]
    second_number = args[1]
    result = first_number + second_number
    await util.say(ctx.channel, "Is " + str(result))


@commands.command()
async def wish(ctx, *args, **details):
    """
    [CMD_KEY]wish
    
    Does this increase the chance of a quest spawn?!
    
    Who knows?
    
    Me.
    
    """

    player = details["author"]
    player.quest_spawn_build_up += 0.000000001


@commands.command(permission=Permission.DUEUTIL_MOD, args_pattern="SSSSIP?")
async def uploadbg(ctx, *args, **details):
    """
    
    [CMD_KEY]uploadbg (a bunch of args)
    
    Takes:
      icon
      name
      desc
      url
      price
      
    in that order.
    
    NOTE: Make event/shitty backgrounds (xmas) etc **free** (so we can delete them)
    
    """

    submitter = None
    if len(args) == 6:
        submitter = args[5]

    icon = args[0]
    if not util.char_is_emoji(icon):
        raise util.DueUtilException(ctx.channel, "Icon must be emoji!")
    description = args[2]
    price = args[4]

    name = util.filter_string(args[1])
    if name != args[1]:
        raise util.DueUtilException(ctx.channel, "Invalid background name!")
    name = re.sub(' +', ' ', name)

    if name.lower() in players.backgrounds:
        raise util.DueUtilException(ctx.channel, "That background name has already been used!")

    if price < 0:
        raise util.DueUtilException(ctx.channel, "Cannot have a negative background price!")

    url = args[3]
    image = await imagehelper.load_image_url(url, raw=True)
    if image is None:
        raise util.DueUtilException(ctx.channel, "Failed to load image!")

    if not imagehelper.has_dimensions(image, (256, 299)):
        raise util.DueUtilException(ctx.channel, "Image must be ``256*299``!")

    image_name = name.lower().replace(' ', '_') + ".png"
    image.save('backgrounds/' + image_name)

    with open('backgrounds/backgrounds.json', 'r+') as backgrounds_file:
        backgrounds = json.load(backgrounds_file)
        backgrounds[name.lower()] = {"name": name, "icon": icon, "description": description, "image": image_name,
                                     "price": price}
        backgrounds_file.seek(0)
        backgrounds_file.truncate()
        json.dump(backgrounds, backgrounds_file, indent=4)

    players.backgrounds.load_backgrounds()

    await util.say(ctx.channel, ":white_check_mark: Background **" + name + "** has been uploaded!")
    await util.duelogger.info("**%s** added the background **%s**" % (details["author"].name_clean, name))

    if submitter is not None:
        await awards.give_award(ctx.channel, submitter, "BgAccepted", "Background Accepted!")


@commands.command(permission=Permission.DUEUTIL_MOD, args_pattern="S")
async def testbg(ctx, *args, **details):
    """
    [CMD_KEY]testbg (image url)

    Tests if a background is the correct dimensions.
    
    """

    url = args[0]
    image = await imagehelper.load_image_url(url)
    if image is None:
        raise util.DueUtilException(ctx.channel, "Failed to load image!")

    if not imagehelper.has_dimensions(image, (256, 299)):
        width, height = image.size
        await util.say(ctx.channel, (":thumbsdown: **That does not meet the requirements!**\n"
                                     + "The tested image had the dimensions ``" + str(width)
                                     + "*" + str(height) + "``!\n"
                                     + "It should be ``256*299``!"))
    else:
        await util.say(ctx.channel, (":thumbsup: **That looks good to me!**\n"
                                     + "P.s. I can't check for low quality images!"))


@commands.command(permission=Permission.DUEUTIL_MOD, args_pattern="S")
async def deletebg(ctx, *args, **details):
    """
    [CMD_KEY]deletebg (background name)
    
    Deletes a background.
    
    DO NOT DO THIS UNLESS THE BACKGROUND IS FREE
    
    """

    background_to_delete = args[0].lower()

    if background_to_delete not in players.backgrounds:
        raise util.DueUtilException(ctx.channel, "Background not found!")
    if background_to_delete == "default":
        raise util.DueUtilException(ctx.channel, "Can't delete default background!")
    background = players.backgrounds[background_to_delete]

    with open('backgrounds/backgrounds.json', 'r+') as backgrounds_file:
        backgrounds = json.load(backgrounds_file)
        del backgrounds[background_to_delete]
        backgrounds_file.seek(0)
        backgrounds_file.truncate()
        json.dump(backgrounds, backgrounds_file, indent=4)
    os.remove("backgrounds/" + background["image"])

    players.backgrounds.load_backgrounds()

    await util.say(ctx.channel, ":wastebasket: Background **" + background.name_clean + "** has been deleted!")
    await util.duelogger.info(
        "**%s** deleted the background **%s**" % (details["author"].name_clean, background.name_clean))


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="S")
async def dueeval(ctx, *args, **details):
    """
    For 1337 haxors only! Go away!
    """

    player = details["author"]
    # print(player.last_message_hashes)
    try:
        await util.say(ctx.channel, ":ferris_wheel: Eval...\n"
                                    "**Result** ```" + str(eval(args[0])) + "```")
    except Exception as eval_exception:
        await util.say(ctx.channel, (":cry: Could not evaluate!\n"
                                     + "``%s``" % eval_exception))


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="PS")
async def sudo(ctx, *args, **details):
    """
    [CMD_KEY]sudo victim command
    
    Infect a victims mind to make them run any command you like!
    """

    try:
        victim = args[0]
        ctx.author = ctx.server.get_member(victim.id)
        ctx.content = args[1]
        await util.say(ctx.channel, ":smiling_imp: Sudoing **" + victim.name_clean + "**!")
        await events.command_event(ctx)
    except util.DueUtilException as command_failed:
        raise util.DueUtilException(ctx.channel, 'Sudo failed! "%s"' % command_failed.message)


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="PC")
async def setpermlevel(ctx, *args, **details):
    player = args[0]
    member = discord.Member(user={"id": player.id})
    permission_index = args[1] - 1
    permissions = dueutil.permissions.permissions
    if permission_index < len(permissions):
        permission = permissions[permission_index]
        dueutil.permissions.give_permission(member, permission)
        await util.say(ctx.channel,
                       "**" + player.name_clean + "** permission level set to ``" + permission.value[1] + "``.")
        if permission == Permission.DUEUTIL_MOD:
            await awards.give_award(ctx.channel, player, "Mod", "Become an mod!")
            await util.duelogger.info("**%s** is now a DueUtil mod!" % player.name_clean)
        elif "Mod" in player.awards:
            player.awards.remove("Mod")
        if permission == Permission.DUEUTIL_ADMIN:
            await awards.give_award(ctx.channel, player, "Admin", "Become an admin!")
            await util.duelogger.info("**%s** is now a DueUtil admin!" % player.name_clean)
        elif "Admin" in player.awards:
            player.awards.remove("Admin")
    else:
        raise util.DueUtilException(ctx.channel, "Permission not found")


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="P")
async def ban(ctx, *args, **details):
    player = args[0]
    member = discord.Member(user={"id": player.id})
    dueutil.permissions.give_permission(member, Permission.BANNED)
    await util.say(ctx.channel, ":hammer: **" + player.name_clean + "** banned!")
    await util.duelogger.concern("**%s** has been banned!" % player.name_clean)


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="P")
async def unban(ctx, *args, **details):
    player = args[0]
    member = discord.Member(user={"id": player.id})
    dueutil.permissions.give_permission(member, Permission.ANYONE)
    await util.say(ctx.channel, ":unicorn: **" + player.name_clean + "** has been unbanned!")
    await util.duelogger.info("**%s** has been unbanned" % player.name_clean)


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="P")
async def toggledonor(ctx, *args, **details):
    player = args[0]
    player.donor = not player.donor
    if player.donor:
        await util.say(ctx.channel, "**" + player.name_clean + "** is now a donor!")
    else:
        await util.say(ctx.channel, "**" + player.name_clean + "** is nolonger donor")


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern=None)
async def duereload(ctx, *args, **details):
    await util.say(ctx.channel, ":ferris_wheel: Reloading DueUtil modules!")
    await util.duelogger.concern("DueUtil Reloading!")
    raise util.DueReloadException(ctx.channel)


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern="PI")
async def givecash(ctx, *args, **details):
    player = args[0]
    amount = args[1]
    player.money += amount
    amount_str = util.format_number(abs(amount), money=True, full_precision=True)
    if amount >= 0:
        await util.say(ctx.channel,
                       "Added ``" + amount_str + "`` to **" + player.get_name_possession_clean() + "** account!")
    else:
        await util.say(ctx.channel,
                       "Subtracted ``" + amount_str + "`` from **" + player.get_name_possession_clean() + "** account!")
    player.save()


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern=None)
async def updateleaderboard(ctx, *args, **details):
    leaderboards.last_leaderboard_update = 0
    await leaderboards.update_leaderboards(ctx)
    await util.say(ctx.channel, ":ferris_wheel: Updating leaderboard!")


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern=None)
async def updatebot(ctx, *args, **details):
    """
    [CMD_KEY]updatebot
    
    Updates DueUtil
    
    """

    try:
        update_result = subprocess.check_output(['bash', 'update_script.sh'])
    except subprocess.CalledProcessError as updateexc:
        update_result = updateexc.output
    update_result = update_result.decode("utf-8")
    if len(update_result.strip()) == 0:
        update_result = "No output."
    update_embed = discord.Embed(title=":gear: Updating DueUtil!", type="rich", color=gconf.EMBED_COLOUR)
    update_embed.description = "Pulling lastest version from **GitLab**!"
    update_embed.add_field(name='Changes', value='```' + update_result + '```', inline=False)
    await util.say(ctx.channel, embed=update_embed)
    update_result = update_result.strip()
    if not (update_result.endswith("is up to date.") or update_result.endswith("up-to-date.")):
        await util.duelogger.concern("DueUtil updating!")
        os._exit(1)


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern=None)
async def stopbot(ctx, *args, **details):
    await util.say(ctx.channel, ":wave: Stopping DueUtil!")
    await util.duelogger.concern("DueUtil shutting down!")
    os._exit(0)


@commands.command(permission=Permission.DUEUTIL_ADMIN, args_pattern=None)
async def restartbot(ctx, *args, **details):
    await util.say(ctx.channel, ":ferris_wheel: Restarting DueUtil!")
    await util.duelogger.concern("DueUtil restarting!!")
    os._exit(1)
