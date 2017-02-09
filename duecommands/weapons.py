import discord;
from fun import game,players;
from botstuff import commands,util,imagehelper;

@commands.command()
async def myweapons(ctx,*args):
  
    """
    [CMD_KEY]myweapons
    
    Shows the contents of your weapon inventory.
    
    """
         
    await show_weapons(ctx,game.Player.find_player(ctx.author.id),False);

@commands.command()
async def shop(ctx,*args):
  
    """
    [CMD_KEY]shop (page number)
    
    Shows DueUtil's weapon store!
    
    """
    await shop(ctx);

@commands.command(admin_only=True,args_pattern='SSSCC')
async def createweapon(ctx,*args):
    
    """
    [CMD_KEY]createweapon icon "weapon name" "hit text" damage accy
    
    Creates a weapon for the server shop!
    
    Example usage: 
    
    [CMD_KEY]createweapon ! "Laser" "FIRES THEIR LAZOR AT" 100 50
    
    Note: The weapon wielder's name will appear before the hit text
    and the victim after.
    
    E.g. If I (MacDue) used the laser gun on MrAwais it would say:
    
    "MacDue FIRES THEIR LAZOR AT MrAwais"
    
    """
