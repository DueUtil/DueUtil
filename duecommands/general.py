import due_battles_quests as quests;
import util_due as util;
from commands.util import commands

@commands.command()
async def myinfo(ctx,*args):
  
    """
    Shows your info!
    """
    
    await quests.display_stats_image(quests.Player.find_player(ctx.author.id), None,ctx);

@commands.command()
async def resetme(ctx,*args): 
    player = Player.find_player(ctx.author.id);
    player.reset();
    await util.say(ctx.channel, "Your user has been reset.");
    if util.is_mod(player.user_id):
        await give_award(message,player,22,"Become an mod!")
    if util.is_admin(player.userid):
        await give_award(message,player,21,"Become an admin!")       

@commands.command()
async def myweapons(ctx,*args):
    await show_weapons(ctx,Player.find_player(ctx.author.id),False);

@commands.command()
async def shop(ctx,*args):
    await shop(ctx);

@commands.command()
async def benfont(ctx,*args):
    player = Player.find_player(ctx.author.id);
    player.benfont = not player.benfont;
    player.save();
    if(player.benfont):
        await util.get_client(ctx.server.id).send_file(ctx.channel,'images/nod.gif');
        await give_award(ctx, player, 16, "ONE TRUE *type* FONT")

@commands.command()
async def mywagers(ctx,*args):      
    player = Player.find_player(ctx.author.id);
    WagerT = "```\n" + player.name + "'s received wagers\n";
    if(len(player.battlers) > 0):
        for x in range(0, len(player.battlers)):
            WagerT = WagerT + str(x + 1) + ". $" +  util.to_money(player.battlers[x].wager,False) + " from " + findPlayer(player.battlers[x].senderID).name + ".\n"
    else:
        WagerT = WagerT + "You have no requests!\n";
    WagerT = WagerT + "Do " + command_key + "acceptwager [Wager Num] to accept a wager.\n";
    WagerT = WagerT + "Do " + command_key + "declinewager [Wager Num] to decline a wager.\n```";
    await get_client(message.server.id).send_message(message.channel, WagerT);

@commands.command()
async def sendcash(ctx,*args):
    sender = Player.find_player(ctx.author.id);
    mentions = message.raw_mentions;
    if(len(mentions) < 1):
        await get_client(message.server.id).send_message(message.channel, ":bangbang: **You must mention one player!**");
        return True;
    elif (len(mentions) > 1):
        await get_client(message.server.id).send_message(message.channel, ":bangbang: **You must mention only one player!**");
        return True;
    try:
        cmd = util.clearmentions(message.content);
        args = re.sub("\s\s+" , " ", cmd).split(sep =" ",maxsplit=2);
        amount = int(args[1]);
        other =findPlayer(mentions[0]);
        if(other == None):
            await get_client(message.server.id).send_message(message.channel, "**"+util.get_server_name(message,mentions[0])+"** has not joined!");
            return True;
        if(other.userid == sender.userid):
            await get_client(message.server.id).send_message(message.channel, ":bangbang: **There is no reason to send money to yourself!**");
            return True;
        if(amount <= 0):
            await get_client(message.server.id).send_message(message.channel, ":bangbang: **You must send at least $1!**");
            return True;
        if(sender.money - amount < 0):
            if(sender.money > 0):
                await get_client(message.server.id).send_message(message.channel, "You do not have **$"+ util.to_money(amount,False)+"**! The maximum you can transfer is **$"+ util.to_money(sender.money,False)+"**");
            else:
                await get_client(message.server.id).send_message(message.channel, "You do not have any money to transfer!");
            return True
        max_receive =  int(max_value_for_player(other)*10);
        if(amount > max_receive):
            await get_client(message.server.id).send_message(message.channel, "**$"+util.to_money(amount,False)+"** is more than ten times **"+other.name+"**'s limit!\nThe maximum **"+other.name+"** can receive is **$"+util.to_money(max_receive,False)+"**!");
            return True;
        sender.money = sender.money - amount;
        other.money = other.money + amount;
        savePlayer(sender);
        savePlayer(other);
        money_transferred = money_transferred + amount;
        print(filter_func(other.name)+" ("+other.userid+") has received $"+util.to_money(amount,False)+" from "+filter_func(sender.name)+" ("+sender.userid+").");
        msg ="";
        if(amount >= 50):
            await give_award(message, sender, 17, "Sugar daddy!")
        if(len(args) == 3 and len(args[2].strip()) > 0):
            msg = "**Attached note**: ```"+args[2]+" ```\n";
        await get_client(message.server.id).send_message(message.channel, ":money_with_wings: **Transaction complete!**\n**"+sender.name+ "** sent $"+ util.to_money(amount,False)+" to **"+other.name+"**\n"+msg+"ᴾˡᵉᵃˢᵉ ᵏᵉᵉᵖ ᵗʰᶦˢ ʳᵉᶜᵉᶦᵖᵗ ᶠᵒʳ ʸᵒᵘʳ ʳᵉᶜᵒʳᵈˢ");
    except:
        await get_client(message.server.id).send_message(message.channel, ":bangbang: **I don't understand your arguments**");
