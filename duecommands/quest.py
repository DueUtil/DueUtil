import discord
from fun import quests, game, battles, imagehelper, weapons
from botstuff import commands, util
from botstuff.permissions import Permission

@commands.command(permission = Permission.DUEUTIL_MOD,args_pattern="S?P?C?I?I?R?",hidden=True)
async def spawnquest(ctx,*args,**details):
    
    """
    [CMD_KEY]spawnquest (name) (@user) (level) (money,wep damage,wep accy)
    
    A command for TESTING only please (awais) do not abuse this power.
    All arguments are optional however the final three must all be entered
    to use them. 
    
    """
  
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
        await util.say(ctx.channel,":cloud_lightning: Spawned **"+quest.name_clean+"** [Level "+str(active_quest.level)+"]")
    except:
        raise util.DueUtilException(ctx.channel,"Failed to spawn quest!")
  
@commands.command(args_pattern='C')
@commands.imagecommand()
async def questinfo(ctx,*args,**details): 
    
    """
    [CMD_KEY]questinfo index
    
    Shows a simple stats page for the quest
    """
  
    player = details["author"]
    quest_index = args[0]-1
    if quest_index >= 0 and quest_index < len(player.quests):
        await imagehelper.quest_screen(ctx.channel,player.quests[quest_index])
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!")

@commands.command(args_pattern='C?')
@commands.imagecommand()
async def myquests(ctx,*args,**details): 
  
    """
    [CMD_KEY]myquests
    
    Shows the list of active quests you have pending.
    
    """
    
    player = details["author"]
    if len(args) == 0:
        page = 0
    else:
        page = args[0]-1
    if page > len(player.quests)/5:
        raise util.DueUtilException(ctx.channel,"Page not found")
    await imagehelper.quests_screen(ctx.channel,player,page)

@commands.command(args_pattern='C')
async def acceptquest(ctx,*args,**details):
  
    """
    [CMD_KEY]acceptquest (quest number)

    You know what to do. Spam ``[CMD_KEY]acceptquest 1``!
    
    """
    
    player = details["author"]
    quest_index = args[0] - 1
    if quest_index >= len(player.quests):
        raise util.DueUtilException(ctx.channel,"Quest not found!")
    if player.money - player.quests[quest_index].money // 2 < 0:
        raise util.DueUtilException(ctx.channel,"You can't afford the risk!")
    if player.quests_completed_today >= game.MAX_DAILY_QUESTS:
        raise util.DueUtilException(ctx.channel,"You can't do more than 50 quests a day!")

    quest = player.quests.pop(quest_index)
    battle_details = battles.get_battle_log(player_one=player,player_two=quest,p2_prefix="the ")
    battle_log = battle_details[0]
    turns = battle_details[1]
    winner = battle_details[2]
    if winner != player:
        battle_log.add_field(name = "Quest results", value = (":skull: **"+player.name_clean+"** lost to the **"+quest.name_clean+"** and dropped ``"
                                                              +util.format_number(quest.money//2,full_precision=True,money=True)+"``"),inline=False)
    else:
        reward = (":sparkles: **"+player.name_clean+"** defeated the **"+quest.name+"** and was rewarded with ``"
                  +util.format_number(quest.money,full_precision=True,money=True)+"``\n")
        attr_gain = lambda stat : (stat + quest.money**0.5/4) * quest.level/(10*player.level)
        add_attack = min(attr_gain(quest.attack),100)
        add_strg = min(attr_gain(quest.strg),100)
        add_accy = min(attr_gain(quest.accy),100)

        stats = ":crossed_swords:+%.2f:muscle:+%.2f:dart:+%.2f" %(add_attack,add_strg,add_accy)
        battle_log.add_field(name = "Quest results", value = reward + stats,inline=False)
        
        player.progress(add_attack,add_strg,add_accy,max_attr=100,max_exp=10000)
        quest_info = quest.info
        if quest_info != None:
            quest_info.times_beaten += 1
            quest_info.save()
        await game.check_for_level_up(ctx,player)
    player.save()
    await imagehelper.battle_screen(ctx.channel,player,quest)
    await util.say(ctx.channel,embed=battle_log)
 
@commands.command(args_pattern='C?')
async def declinequest(ctx,*args,**details):
  
    """
    [CMD_KEY]declinequest index

    Declines a quest because you're too wimpy to accept it.
    
    """
    
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
        await util.say(ctx.channel, ("**"+player.name_clean +"** declined to " 
                                     + quest_task + " **" + quest.name_clean 
                                     + " [Level " + str(qT.level) + "]**!"))
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!")

@commands.command(args_pattern='SRRRRS?S?S?R?')
async def createquest(ctx,*args,**details):
    
    """
    [CMD_KEY]createquest
    
    Hard mode: figure it out yourself.
    
    I'm going to bed.
    
    cyka blyat
    """
    
    extras = dict()
    if len(args) >= 6:
        extras['task'] = args[5]
    if len(args) >= 7:
        extras['weapon_id'] = weapons.get_weapon_for_server(ctx.server,args[6]).w_id
    if len(args) == 8:
        extras['image_url'] = args[7]
    if len(args) == 9:
        extras['spawn_chance'] = args[8]
    
    new_quest = quests.Quest(*args[:5],**extras,ctx=ctx)
    await util.say(ctx.channel,":white_check_mark: "+util.ultra_escape_string(new_quest.task)+ " **"+new_quest.name_clean+"** is now active!")
    
@commands.command(permission = Permission.SERVER_ADMIN,args_pattern='C?')
async def serverquests(ctx,*args,**details):
  
    page = 0
    if len(args) == 1:
        page = args[0] - 1
    embed = discord.Embed(title=(":crossed_swords: Quests on "+details["server_name_clean"]
                                 +(" : Page "+str(page+1) if page > 0 else "")),type="rich",color=16038978)
    page_size = 12
    quests_list = list(quests.get_server_quest_list(ctx.server).values())
    if page * page_size >= len(quests_list):
        raise util.DueUtilException(None,"Page not found")
    quest_index = 0
    for quest_index in range(page_size*page,page_size*page+page_size):
        if quest_index >= len(quests_list):
            break
        quest = quests_list[quest_index]
        embed.add_field(name = quest.name_clean, value = "Completed "+str(quest.times_beaten)+" time"+("s" if quest.times_beaten != 1 else ""))
    if quest_index < len(quests_list) - 1:
        embed.set_footer(text="But wait there more! Do "+details["cmd_key"]+"serverquests "+str(page+2))
    else:
        embed.set_footer(text="That's all!")
    await util.say(ctx.channel,embed=embed)
