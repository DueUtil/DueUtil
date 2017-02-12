import discord;
from fun import game,players;
from botstuff import commands,util,imagehelper;

@commands.command(args_pattern=None)
@commands.imagecommand()
async def myinfo(ctx,*args):
  
    """
    [CMD_KEY]myinfo
    
    Shows your info!
    
    """
    
    await imagehelper.stats_screen(ctx.channel,game.Players.find_player(ctx.author.id));
    
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
    
    await show_awards(ctx,game.Players.find_player(ctx.author.id),*args);
    
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
    
    player = game.Players.find_player(ctx.author.id);
    player.reset();
    await util.say(ctx.channel, "Your user has been reset.");
    if util.is_mod(player.user_id):
        await give_award(message,player,22,"Become an mod!")
    if util.is_admin(player.userid):
        await give_award(message,player,21,"Become an admin!")    
        
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
    
    sender = game.Players.find_player(ctx.author.id);
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
        return;
        
    max_receive =  int(receiver.item_value_limit*10);
    
    amount_string = util.format_number(transaction_amount,money=True,full_precision=True);
    
    if transaction_amount > max_receive:
        await util.say(ctx.channel, ("**"+amount_string
                                     +"** is more than ten times **"+receiver.name
                                     +"**'s limit!\nThe maximum **"+receiver.name
                                     +"** can receive is **"
                                     +util.format_number(max_receive,money=True)+"**!"));
        return;
        
    sender.money -= transaction_amount;
    receiver.money += transaction_amount;
    
    sender.save();
    receiver.save();
    
    game.Stats.money_transferred += transaction_amount;
    if transaction_amount >= 50:
        await players.give_award(ctx.channel, sender, 17, "Sugar daddy!");
        
    transaction_log = discord.Embed(title=":money_with_wings: Transaction complete!",type="rich",color=16038978);
    transaction_log.add_field(name="Sender:",value=sender.name);
    transaction_log.add_field(name="Recipient:",value=receiver.name);
    transaction_log.add_field(name="Transaction amount (DUT):",value=amount_string,inline=False);
    if len(args) > 2:
      transaction_log.add_field(name=":pencil: Attached note:",value=args[2],inline=False);
    transaction_log.set_footer(text="Please keep this receipt for your records.");
    
    await util.say(ctx.channel,embed=transaction_log);
  
@commands.command()
async def mywagers(ctx,*args):    
  
    """
    [CMD_KEY]mywagers
    
    Shows your active wager requests.
    Note: Wagers expire if you don't accept them within one hour.
    
    """
    
    player = game.Players.find_player(ctx.author.id);
    WagerT = "```\n" + player.name + "'s received wagers\n";
    if(len(player.battlers) > 0):
        for x in range(0, len(player.battlers)):
            WagerT = WagerT + str(x + 1) + ". $" +  util.to_money(player.battlers[x].wager,False) + " from " + findPlayer(player.battlers[x].senderID).name + ".\n"
    else:
        WagerT = WagerT + "You have no requests!\n";
    WagerT = WagerT + "Do " + command_key + "acceptwager [Wager Num] to accept a wager.\n";
    WagerT = WagerT + "Do " + command_key + "declinewager [Wager Num] to decline a wager.\n```";
    await get_client(message.server.id).send_message(message.channel, WagerT);
    
@commands.command(hidden=True)
async def benfont(ctx,*args):
  
    """
    [CMD_KEY]benfont 
    
    Shhhhh...
    
    """
    
    player = game.Players.find_player(ctx.author.id);
    player.benfont = not player.benfont;
    player.save();
    if(player.benfont):
        await util.get_client(ctx.server.id).send_file(ctx.channel,'images/nod.gif');
        await players.give_award(ctx.channel, player, 16, "ONE TRUE *type* FONT")

