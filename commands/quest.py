from due_battles_quests import *;
import util_due as util;

async def questinfo(ctx,*args): 
    player = Player.find_player(ctx.author.id);
    quest_index = int(args[0]);
    if (quest_index - 1) >= 0 and (quest_index - 1) <= len(player.quests) - 1:
        await displayStatsImage(player.quests[q - 1], True, message);
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!");
        
async def myquests(ctx,*args): 
    await showQuests(message);
    
async def acceptquest(ctx, **args):
    player = Player.find_player(ctx.author.id);
    quest_index = int(args[0]);
    if (quest_index - 1) >= 0 and (quest_index - 1) <= len(player.quests) - 1:
        if(player.money - int((player.quests[quest_index - 1].money) / 2)) >= 0:
            if(player.quests_completed_today < 50):
                questToBattle = player.quests[quest_index - 1];
                del player.quests[quest_index - 1];
                await battle(message, [message.author.id, questToBattle], questToBattle.money, True);
                player.save();
            else:
                raise util.DueUtilException(ctx.channel,"You can't do more than 50 quests a day!");
        else:
            raise util.DueUtilException(ctx.channel,"You can't afford the risk!");
    else:
        raise util.DueUtilException(ctx.channel,"Quest not found!");
        
async def declinequest(ctx,*args):
    player = Player.find_player(ctx.author.id);
    quest_index = int(args[0]);
    
    if (quest_index - 1) >= 0 and (quest_index - 1) <= len(player.quests) - 1:
        quest = player.quests[quest_index - 1];
        del player.quests[quest_index - 1];
        player.save();
        try:
            main_quest = get_game_quest_from_id(qT.qID);
            if(main_quest != None):
                questT = main_quest.quest;
            else:
                questT = "do a long forgotten quest:";
        except:
            questT = "do a long forgotten quest:";
        await get_client(message.server.id).send_message(message.channel, "**"+player.name + "** declined to " + questT + " **" + qT.name + " [Level " + str(qT.level) + "]**!");
    else:
        await get_client(message.server.id).send_message(message.channel, ":bangbang:  **Quest not found!**");

