from due_battles_quests import *;
import util_due as util;

async def resetme(ctx,*args): 
    player = Player.find_player(ctx.author.id);
    player.reset();
    player.save();
    await util.say(ctx.channel, "Your user has been reset.");
    if util.is_mod(player.user_id):
        await give_award(message,player,22,"Become an mod!")
    if util.is_admin(player.userid):
        await give_award(message,player,21,"Become an admin!")       

async def myweapons(ctx,*args):
    await show_weapons(message,findPlayer(message.author.id),False);

async def shop(ctx,*args):
    await shop(message);
