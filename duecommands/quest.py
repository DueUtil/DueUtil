from fun import quests, game, battles, imagehelper
from botstuff import commands, util

@commands.command(args_pattern="S?P?C?",hidden=True)
async def spawnquest(ctx,*args,**details):
    if len(args) == 0:
        player = details["author"]
        quest = quests.get_random_quest_in_channel(ctx.channel)
    else:
        player = args[1]
        quest_name = args[0].lower()
        quest = quests.get_quest_from_id(ctx.server.id+"/"+quest_name)
    try:
        active_quest = quests.ActiveQuest(quest.q_id,player)
        if len(args) == 3:
            active_quest.level = args[2]
            active_quest.__calculate_stats__()
        player.save()
        await util.say(ctx.channel,":cloud_lightning: Spawned **"+quest.name+"** [Level "+str(active_quest.level)+"]")
    except:
        raise util.DueUtilException(ctx.channel,"Failed to spawn quest!")
  
@commands.command(args_pattern='C')
@commands.imagecommand()
async def questinfo(ctx,*args,**details): 
    player = details["author"]
    quest_index = args[0]-1
    if quest_index >= 0 and quest_index < len(player.quests):
        await imagehelper.quest_screen(ctx.channel,player.quests[quest_index])
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!")

@commands.command(args_pattern='C?')
async def myquests(ctx,*args,**details): 
    player = details["author"]
    if len(args) == 0:
        page = 0
    else:
        page = args[0]-1
        
    if page > len(player.quests)/5:
        raise util.DueUtilException(ctx.channel,"Page not found")
    await imagehelper.quests_screen(ctx.channel,player,page)

@commands.command()
async def acceptquest(ctx, **args):
    player = details["author"]
    quest_index = args[0] - 1
    if quest_index >= 0 and quest_index < len(player.quests):
        if player.money - player.quests[quest_index].money // 2 >= 0:
            if player.quests_completed_today < game.MAX_DAILY_QUESTS:
                quest = player.quests[quest_index]
                del player.quests[quest_index]
                await battles.battle(message, [message.author.id, questToBattle], questToBattle.money, True)
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
    quest_list = quests.get_server_quest_list(ctx.server)
    
