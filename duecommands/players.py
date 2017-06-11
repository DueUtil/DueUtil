import discord
import fun.awards
from fun import imagehelper
from fun import players
from fun import stats
from fun import misc
from fun import players_abstract
from botstuff import commands,util,permissions
from botstuff.permissions import Permission
import generalconfig as gconf 

@commands.command(args_pattern="S?")
async def battlename(ctx,*args,**details):
    
    """
    [CMD_KEY]battlename (name)
    
    Sets your name in DueUtil.
    To reset your name to your discord name run the
    command with no arguments
    
    """
    player = details["author"]
    if len(args) == 1:
        name = args[0]
        name_len_range = players.Player.NAME_LENGTH_RANGE
        if len(name) not in name_len_range:
            raise util.DueUtilException(ctx.channel,("Battle name must be between **"
                                        +str(min(name_len_range))+"-"+str(max(name_len_range))+"** characters long!"))
        player.name = name
    else:
        player.name = details["author_name"]
    player.save()
    await util.say(ctx.channel,"Your battle name has been set to **"+player.name_clean+"**!")
    
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

@commands.command(args_pattern="S?")
async def resetme(ctx,*args,**details): 
  
    """
    [CMD_KEY]resetme
    
    Resets all your stats & any customization.
    This cannot be reversed!
    
    """
    if len(args) == 1 and args[0].lower() == "cnf":
        player = details["author"]
        player.reset(ctx.author)
        await util.say(ctx.channel, "Your user has been reset.")
        if permissions.has_special_permission(ctx.author,Permission.DUEUTIL_MOD):
            await fun.awards.give_award(ctx.channel,player,"Mod","Become an mod!")
        elif permissions.has_special_permission(ctx.author,Permission.DUEUTIL_ADMIN):
            await fun.awards.give_award(ctx.channel,player,"Admin","Become an admin!")    
    else:
        await util.say(ctx.channel,("Are you sure?! This will **__permanently__** reset your user!"
                                    +"\nDo ``"+details["cmd_key"]+"resetme cnf`` if you're sure!"))
        
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
    amount_string = util.format_number(transaction_amount,money=True,full_precision=True)
    
    if receiver.id == sender.id:
        raise util.DueUtilException(ctx.channel,"There is no reason to send money to yourself!")
   
    if sender.money - transaction_amount < 0:
        if sender.money > 0:
            await util.say(ctx.channel, ("You do not have **"+amount_string+"**!\n"
                                        "The maximum you can transfer is **"
                                        + util.format_number(sender.money,money = True,full_precision= True)+"**"))
        else:
            await util.say(ctx.channel,"You do not have any money to transfer!")
        return
        
    max_receive =  int(receiver.item_value_limit*10)
    
    
    if transaction_amount > max_receive:
        await util.say(ctx.channel, ("**"+amount_string
                                     +"** is more than ten times **"+receiver.name_clean
                                     +"**'s limit!\nThe maximum **"+receiver.name_clean
                                     +"** can receive is **"
                                     +util.format_number(max_receive,money=True,full_precision = True)+"**!"))
        return
        
    sender.money -= transaction_amount
    receiver.money += transaction_amount
    
    sender.save()
    receiver.save()
    
    stats.increment_stat(stats.Stat.MONEY_TRANSFERRED,transaction_amount)
    if transaction_amount >= 50:
        await fun.awards.give_award(ctx.channel, sender, "SugarDaddy", "Sugar daddy!")
        
    transaction_log = discord.Embed(title=":money_with_wings: Transaction complete!",type="rich",color=gconf.EMBED_COLOUR)
    transaction_log.add_field(name="Sender:",value=sender.name_clean)
    transaction_log.add_field(name="Recipient:",value=receiver.name_clean)
    transaction_log.add_field(name="Transaction amount (DUT):",value=amount_string,inline=False)
    if len(args) > 2:
      transaction_log.add_field(name=":pencil: Attached note:",value=args[2],inline=False)
    transaction_log.set_footer(text="Please keep this receipt for your records.")
    
    await util.say(ctx.channel,embed=transaction_log)
    
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
@players_abstract.item_preview
def mythemes(player):
  
    """
    [CMD_KEY]mythemes (optional theme name)
    
    Shows the amazing themes you can use on your profile.
    If you use this command with a theme name you can get a preview of the theme!
    
    """
    return {"thing_type":"theme",
            "thing_list":list(player.get_owned_themes().values()),
            "thing_lister":theme_page,
            "my_command":"mythemes",
            "thing_info":theme_info,
            "thing_getter":players.get_theme}

@commands.command(args_pattern='S')
@players_abstract.item_setter
def settheme(player):
  
    """
    [CMD_KEY]settheme (theme name)
    
    Sets your profile theme
    
    """
    
    return {"thing_type":"theme",
            "thing_getter":players.get_theme,
            "thing_setter":player.set_theme,
            "thing_list":player.themes}

@commands.command(args_pattern='M?')
@players_abstract.item_preview
def mybgs(player):
  
    """
    [CMD_KEY]mybgs (optional theme name)
    
    Shows the backgrounds you've bought!
    
    """
    
    return {"thing_type":"background",
        "thing_list":list(player.get_owned_backgrounds().values()),
        "thing_lister":background_page,
        "my_command":"mybgs",
        "thing_info":background_info,
        "thing_getter":players.get_background}

@commands.command(args_pattern='S')
@players_abstract.item_setter
def setbg(player):
  
    """
    [CMD_KEY]setbg (background name)
    
    Sets your profile background
    
    """

    return {"thing_type":"background",
            "thing_getter":players.get_background,
            "thing_setter":player.set_background,
            "thing_list":player.backgrounds}

@commands.command(args_pattern='M?')
@players_abstract.item_preview
def mybanners(player):
  
    """
    [CMD_KEY]mybanners (optional theme name)
    
    Shows the banners you've bought!
    
    """
    return {"thing_type":"banner",
        "thing_list":list(player.get_owned_banners().values()),
        "thing_lister":banner_page,
        "my_command":"mybanners",
        "thing_info":banner_info,
        "thing_getter":players.get_banner}


@commands.command(args_pattern='S')
@players_abstract.item_setter
def setbanner(player):
  
    """
    [CMD_KEY]setbanner (banner name)
    
    Sets your profile banner
    
    """

    return {"thing_type":"banner",
            "thing_getter":players.get_banner,
            "thing_setter":player.set_banner,
            "thing_list":player.banner}
    
# Part of the shop buy command
@misc.paginator
def theme_page(themes_embed,theme,**extras):
    price_divisor = extras.get('price_divisor',1)
    themes_embed.add_field(name=theme["icon"]+" | "+theme["name"],value=(theme["description"]+"\n ``"
                           +util.format_number(theme["price"]//price_divisor,money=True,full_precision=True)+"``"))
          
@misc.paginator
def background_page(backgrounds_embed,background,**extras):
    price_divisor = extras.get('price_divisor',1)
    backgrounds_embed.add_field(name=background["icon"]+" | "+background["name"],value=(background["description"]+"\n ``"
                           +util.format_number(background["price"]//price_divisor,money=True,full_precision=True)+"``"))
                           
@misc.paginator
def banner_page(banners_embed,banner,**extras):
    price_divisor = extras.get('price_divisor',1)
    banners_embed.add_field(name=banner.icon+" | "+banner.name,value=(banner.description+"\n ``"
                           +util.format_number(banner.price//price_divisor,money=True,full_precision=True)+"``"))
                                                      
def theme_info(theme_name,**details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor',1)
    theme = details.get('theme',players.get_theme(theme_name))
    embed.title = str(theme)
    embed.set_image(url=theme["preview"])
    embed.set_footer(text="Buy this theme for "+util.format_number(theme["price"]//price_divisor,money=True,full_precision=True))
    return embed
    
def background_info(background_name,**details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor',1)
    background = players.get_background(background_name)
    embed.title = str(background)
    embed.set_image(url="https://dueutil.tech/duefiles/backgrounds/"+background["image"])
    embed.set_footer(text="Buy this background for "+util.format_number(background["price"]//price_divisor,money=True,full_precision=True))
    return embed
    
def banner_info(banner_name,**details):
    embed = details["embed"]
    price_divisor = details.get('price_divisor',1)
    banner = players.get_banner(banner_name)
    embed.title = str(banner)
    if banner.donor:
        embed.description = ":star2: This is a __donor__ banner!"
    embed.set_image(url="https://dueutil.tech/duefiles/banners/"+banner.image_name)
    embed.set_footer(text="Buy this banner for "+util.format_number(banner.price//price_divisor,money=True,full_precision=True))
    return embed
