from fun import quests, game, imagehelper
from botstuff import commands, util

@commands.command(args_pattern='I')
async def questinfo(ctx,*args,**details): 
    player = details["author"]
    quest_index = args[0] - 1
    if quest_index >= 0 and quest_index <= len(player.quests) - 1:
        await imagehelper.quest_screen(ctx.channel,player.quests[quest_index])
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!")

@commands.command()
async def myquests(ctx,*args,**details): 
    pass

@commands.command()
async def acceptquest(ctx, **args):
    player = Player.find_player(ctx.author.id)
    quest_index = int(args[0])
    if (quest_index - 1) >= 0 and (quest_index - 1) <= len(player.quests) - 1:
        if(player.money - int((player.quests[quest_index - 1].money) / 2)) >= 0:
            if(player.quests_completed_today < 50):
                questToBattle = player.quests[quest_index - 1]
                del player.quests[quest_index - 1]
                await battle(message, [message.author.id, questToBattle], questToBattle.money, True)
                player.save()
            else:
                raise util.DueUtilException(ctx.channel,"You can't do more than 50 quests a day!")
        else:
            raise util.DueUtilException(ctx.channel,"You can't afford the risk!")
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!")
 
@commands.command()
async def declinequest(ctx,*args,**details):
    player = Player.find_player(ctx.author.id)
    quest_index = int(args[0])
    
    if (quest_index - 1) >= 0 and (quest_index - 1) <= len(player.quests) - 1:
        quest = player.quests[quest_index - 1]
        del player.quests[quest_index - 1]
        player.save()
        try:
            main_quest = get_game_quest_from_id(qT.qID)
            if(main_quest != None):
                questT = main_quest.quest
            else:
                questT = "do a long forgotten quest:"
        except:
            questT = "do a long forgotten quest:"
        await get_client(message.server.id).send_message(message.channel, "**"+player.name + "** declined to " + questT + " **" + qT.name + " [Level " + str(qT.level) + "]**!")
    else:
        await get_client(message.server.id).send_message(message.channel, ":bangbang:  **Quest not found!**")

@commands.command(admin_only=True)
async def serverquests(ctx,*args,**details):
    await show_quest_list(ctx)
