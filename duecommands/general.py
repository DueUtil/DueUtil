from fun import game,players;
from botstuff import commands,util,imagehelper;

@commands.command(args_pattern=None)
@commands.imagecommand()
async def myinfo(ctx,*args):
  
    """
    [CMD_KEY]myinfo
    
    Shows your info!
    
    """
    
    await imagehelper.stats_screen(ctx.channel,game.Player.find_player(ctx.author.id));
    
@commands.command(args_pattern='P')
@commands.imagecommand()
async def info(ctx,*args):
  
    """
    [CMD_KEY]info @player
    
    Shows the info of another player!
    
    """
    
    await imagehelper.stats_screen(ctx.channel,args[0]);
    
    
async def show_awards(ctx,player,*args):
  
    if len(args) == 0:
        page = 0;
    else:
        page = args[0]-1;
        
    if page > len(player.awards)/5:
        raise util.DueUtilException(ctx.channel,"Page not found");
        
    await imagehelper.awards_screen(ctx.channel,player,page);
    
@commands.command(args_pattern='C?')
@commands.imagecommand()
async def myawards(ctx,*args):
  
    """
    [CMD_KEY]myawards (page number)
    
    Shows your awards!
    
    """
    
    await show_awards(ctx,game.Player.find_player(ctx.author.id),*args);
    
@commands.command(args_pattern='PC?')
@commands.imagecommand()
async def awards(ctx,*args):
  
    """
    [CMD_KEY]awards @player (page number)
    
    Shows a players awards!
    
    """  
    
    await show_awards(ctx,args[0],*args[1:]);     

@commands.command()
async def resetme(ctx,*args): 
  
    """
    [CMD_KEY]resetme
    
    Resets all your stats & any customization.
    This cannot be reversed!
    
    """
    
    player = game.Player.find_player(ctx.author.id);
    player.reset();
    await util.say(ctx.channel, "Your user has been reset.");
    if util.is_mod(player.user_id):
        await give_award(message,player,22,"Become an mod!")
    if util.is_admin(player.userid):
        await give_award(message,player,21,"Become an admin!")       

@commands.command()
async def myweapons(ctx,*args):
  
    """
    [CMD_KEY]myweapons
    
    Shows the contents of your weapon inventory.
    
    """
         
    await show_weapons(ctx,Player.find_player(ctx.author.id),False);

@commands.command()
async def shop(ctx,*args):
  
    """
    [CMD_KEY]shop (page number)
    
    Shows DueUtil's weapon store!
    
    """
    await shop(ctx);

@commands.command(hidden=True)
async def benfont(ctx,*args):
  
    """
    [CMD_KEY]benfont 
    
    Shhhhh...
    
    """
    
    player = game.Player.find_player(ctx.author.id);
    player.benfont = not player.benfont;
    player.save();
    if(player.benfont):
        await util.get_client(ctx.server.id).send_file(ctx.channel,'images/nod.gif');
        await players.give_award(ctx.channel, player, 16, "ONE TRUE *type* FONT")

@commands.command()
async def mywagers(ctx,*args):    
  
    """
    [CMD_KEY]mywagers
    
    Shows your active wager requests.
    Note: Wagers expire if you don't accept them within one hour.
    
    """
    
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

@commands.command(args_pattern='PCS?')
async def sendcash(ctx,*args):
  
    """
    [CMD_KEY]sendcash @player amount (optional message)
    
    Sends some cash to another player.
    Note: The maximum amount someone can receive is ten times their limit.
    
    Example usage:
    
    [CMD_KEY]sendcash @MacDue 1000000 "for the lit bot fam"
    
    or
    
    [CMD_KEY]sendcash @MrAwais 1
    
    """
    
    sender = Player.find_player(ctx.author.id);
    receiver = args[0];
    transaction_amount = args[1];
    
    if receiver.user_id == sender.user_id:
        raise util.DueUtilException(ctx.channel,"There is no reason to send money to yourself!");
   
    if sender.money - transaction_amount < 0:
        if sender.money > 0:
            await util.say(ctx.channel, ("You do not have **$"+ util.to_money(amount,False)+"**!"
                                        "The maximum you can transfer is **$"+ util.to_money(sender.money,False)+"**"));
        else:
            await util.say(ctx.channel,"You do not have any money to transfer!");
        
    max_receive =  int(max_value_for_player(other)*10);
    if(amount > max_receive):
        await get_client(message.server.id).send_message(message.channel, "**$"+util.to_money(amount,False)+"** is more than ten times **"+other.name+"**'s limit!\nThe maximum **"+other.name+"** can receive is **$"+util.to_money(max_receive,False)+"**!");
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
