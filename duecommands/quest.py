from fun import quests, game, battles, imagehelper
from botstuff import commands, util
from botstuff.permissions import Permission

@commands.command(args_pattern="S?P?C?I?I?R?",hidden=True)
async def spawnquest(ctx,*args,**details):
    player = details["author"]
    if len(args) == 0:
        quest = quests.get_random_quest_in_channel(ctx.channel)
    else:
        if len(args) >= 2:
            player = args[1]
        quest_name = args[0].lower()
        quest = quests.get_quest_from_id(ctx.server.id+"/"+quest_name)
    try:
        active_quest = quests.ActiveQuest(quest.q_id,player)
        if len(args) >= 3:
            active_quest.level = args[2]
            spoofs = args[3:]
            spoof_values = {}
            if len(spoofs) == 3:
                spoof_values = {'q_money' : spoofs[0], 'w_damage' : spoofs[1], 'w_accy' : spoofs[2]}
            active_quest.__calculate_stats__(**spoof_values)
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
@commands.imagecommand()
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
                await battles.battle(player_one=player,player_two=quest)
                player.save()
            else:
                raise util.DueUtilException(ctx.channel,"You can't do more than 50 quests a day!")
        else:
            raise util.DueUtilException(ctx.channel,"You can't afford the risk!")
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!")
 
@commands.command(args_pattern='C?')
async def declinequest(ctx,*args,**details):
    player = details["author"]
    quest_index = args[0] -1
    if quest_index >= 0 and quest_index  < len(player.quests):
        quest = player.quests[quest_index]
        del player.quests[quest_index]
        player.save()
        quest_info = quest.info
        if quest_info != None:
            quest_task = quest_info.task
        else:
            quest_task = "do a long forgotten quest:"
        await util.say(ctx.channel, ("**"+player.name +"** declined to " 
                                      + quest_task + " **" + quest.name 
                                      + " [Level " + str(qT.level) + "]**!"))
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!")

@commands.command(permission = Permission.SERVER_ADMIN)
async def serverquests(ctx,*args,**details):
    quests.get_server_quest_list(ctx.server)
    
