import discord
import fun.awards
from fun import players, stats, imagehelper, game
from botstuff import commands,util

@commands.command(args_pattern=None)
@commands.imagecommand()
async def myinfo(ctx,*args,**details):
  
    """
    [CMD_KEY]myinfo
    
    Shows your info!
    
    """
    
    await imagehelper.stats_screen(ctx.channel,details["author"])
    
@commands.command(args_pattern='P')
@commands.imagecommand()
async def info(ctx,*args,**details):
  
    """
    [CMD_KEY]info @player
    
    Shows the info of another player!
    
    """
    
    await imagehelper.stats_screen(ctx.channel,args[0])
    
async def show_awards(ctx,player,*args):
  
    if len(args) == 0:
        page = 0
    else:
        page = args[0]-1
        
    if page > len(player.awards)/5:
        raise util.DueUtilException(ctx.channel,"Page not found")
        
    await imagehelper.awards_screen(ctx.channel,player,page)
    
@commands.command(args_pattern='C?')
@commands.imagecommand()
async def myawards(ctx,*args,**details):
  
    """
    [CMD_KEY]myawards (page number)
    
    Shows your awards!
    
    """
    
    await show_awards(ctx,details["author"],*args)
    
@commands.command(args_pattern='PC?')
@commands.imagecommand()
async def awards(ctx,*args,**details):
  
    """
    [CMD_KEY]awards @player (page number)
    
    Shows a players awards!
    
    """  
    
    await show_awards(ctx,args[0],*args[1:]);     

@commands.command()
async def resetme(ctx,*args,**details): 
  
    """
    [CMD_KEY]resetme
    
    Resets all your stats & any customization.
    This cannot be reversed!
    
    """
    
    player = details["author"]
    player.reset(ctx.author)
    await util.say(ctx.channel, "Your user has been reset.")
    if util.is_mod(player.user_id):
        await give_award(message,player,22,"Become an mod!")
    if util.is_admin(player.userid):
        await give_award(message,player,21,"Become an admin!")    
        
@commands.command(args_pattern='PCS?')
async def sendcash(ctx,*args,**details):
  
    """
    [CMD_KEY]sendcash @player amount (optional message)
    
    Sends some cash to another player.
    Note: The maximum amount someone can receive is ten times their limit.
    
    Example usage:
    
    [CMD_KEY]sendcash @MacDue 1000000 "for the lit bot fam"
    
    or
    
    [CMD_KEY]sendcash @MrAwais 1
    
    """
    
    sender = details["author"]
    receiver = args[0]
    transaction_amount = args[1]
    
    if receiver.id == sender.id:
        raise util.DueUtilException(ctx.channel,"There is no reason to send money to yourself!")
   
    if sender.money - transaction_amount < 0:
        if sender.money > 0:
            await util.say(ctx.channel, ("You do not have **$"+ util.to_money(amount,False)+"**!"
                                        "The maximum you can transfer is **$"+ util.to_money(sender.money,False)+"**"))
        else:
            await util.say(ctx.channel,"You do not have any money to transfer!")
        return
        
    max_receive =  int(receiver.item_value_limit*10)
    
    amount_string = util.format_number(transaction_amount,money=True,full_precision=True)
    
    if transaction_amount > max_receive:
        await util.say(ctx.channel, ("**"+amount_string
                                     +"** is more than ten times **"+receiver.name
                                     +"**'s limit!\nThe maximum **"+receiver.name
                                     +"** can receive is **"
                                     +util.format_number(max_receive,money=True)+"**!"))
        return
        
    sender.money -= transaction_amount
    receiver.money += transaction_amount
    
    sender.save()
    receiver.save()
    
    stats.increment_stat(stats.Stat.MONEY_TRANSFERRED,transaction_amount)
    if transaction_amount >= 50:
        await players.give_award(ctx.channel, sender, 17, "Sugar daddy!")
        
    transaction_log = discord.Embed(title=":money_with_wings: Transaction complete!",type="rich",color=16038978)
    transaction_log.add_field(name="Sender:",value=sender.name)
    transaction_log.add_field(name="Recipient:",value=receiver.name)
    transaction_log.add_field(name="Transaction amount (DUT):",value=amount_string,inline=False)
    if len(args) > 2:
      transaction_log.add_field(name=":pencil: Attached note:",value=args[2],inline=False)
    transaction_log.set_footer(text="Please keep this receipt for your records.")
    
    await util.say(ctx.channel,embed=transaction_log)
  
@commands.command()
async def mywagers(ctx,*args,**details):    
  
    """
    [CMD_KEY]mywagers
    
    Shows your active wager requests.
    Note: Wagers expire if you don't accept them within one hour.
    
    """
    
    player = details["author"]
    WagerT = "```\n" + player.name + "'s received wagers\n"
    if(len(player.battlers) > 0):
        for x in range(0, len(player.battlers)):
            WagerT = WagerT + str(x + 1) + ". $" +  util.to_money(player.battlers[x].wager,False) + " from " + findPlayer(player.battlers[x].senderID).name + ".\n"
    else:
        WagerT = WagerT + "You have no requests!\n"
    WagerT = WagerT + "Do " + command_key + "acceptwager [Wager Num] to accept a wager.\n"
    WagerT = WagerT + "Do " + command_key + "declinewager [Wager Num] to decline a wager.\n```"
    await get_client(message.server.id).send_message(message.channel, WagerT)
    
@commands.command(hidden=True)
async def benfont(ctx,*args,**details):
  
    """
    [CMD_KEY]benfont 
    
    Shhhhh...
    
    """
    
    player = details["author"]
    player.benfont = not player.benfont
    player.save()
    if player.benfont:
        await util.get_client(ctx.server.id).send_file(ctx.channel,'images/nod.gif')
        await fun.awards.give_award(ctx.channel, player,"BenFont", "ONE TRUE *type* FONT")
        
# Think about clean up & reuse
@commands.command(args_pattern='M?')
async def mythemes(ctx,*args,**details):
  
    """
    [CMD_KEY]mythemes (optional theme name)
    
    Shows the amazing themes you can use on your profile.
    If you use this command with a theme name you can get a preview of the theme!
    
    """
    
    player = details["author"]
    page = args[0] if len(args) == 1 else 0
    
    if type(page) is int:
      
        themes = list(player.get_owned_themes().values())
        themes_listings = discord.Embed(title="Available themes",type="rich",color=16038978)      
        if 12 * page + 12 < len (themes):
            footer = "But wait there's more! Do "++"mythemes "+str(page+2)
        else:
            footer = 'More themes coming soon!'

        for theme_index in range(12 * page,12 * page + 12):
            if theme_index >= len(themes):
                break
            theme = themes[theme_index]
            themes_listings.add_field(name=theme["icon"]+" | "+theme["name"],value=theme["description"])
        themes_listings.set_footer(text=footer)
        await util.say(ctx.channel,embed=themes_listings)
    else:
        theme = players.get_theme(page)
        if theme == None:
            raise util.DueUtilException(ctx.channel,"Theme not found!")
        theme_info = discord.Embed(title=theme["icon"]+" | "+theme["name"],type="rich",color=16038978)
        theme_info.set_image(url=theme["preview"])
        theme_info.set_footer(text="Do "+details["cmd_key"]+"settheme "+theme["name"].lower()+" to use this theme!")
        await util.say(ctx.channel,embed=theme_info)
         
@commands.command(args_pattern='S')
async def settheme(ctx,*args,**details):
    player = details["author"]
    theme_name = args[0].lower()
    theme = players.get_theme(theme_name)
    if theme != None:
        player.theme_id = theme_name
        player.banner_id = theme["banner"]
        player.backgrounds = theme["background"]
        player.save()
        await util.say(ctx.channel,":white_check_mark: Theme set to **"+theme["name"]+"**")
    else:
        raise util.DueUtilException(ctx.channel,"Theme not found!")
