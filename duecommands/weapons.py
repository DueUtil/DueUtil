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

@commands.command(args_pattern='M?')
async def shop(ctx,*args):
  
    """
    [CMD_KEY]shop (page number) or (weapon name)
    
    Shows DueUtil's weapon store!
    
    Shows information about a weapon in the shop if given a weapon name.
    
    """
    page = args[0] if len(args) == 1 else 0;
    
    if type(page) is int:
    
        shop_weapons = list(game.Weapons.get_weapons_for_server(ctx.server.id).values());

        if 12 * page + 12 < len (shop_weapons):
            footer = "But wait there's more! Do "+util.get_server_cmd_key(ctx.server)+"shop "+str(page+2);
        else:
            footer = 'Want more? Ask an admin on '+ctx.server.name+' to add some!';
    
        shop = discord.Embed(title="DueUtil's Weapon Shop!",type="rich",color=16038978);
        for stock_number in range(12*page,12*page+12):
            if stock_number >= len(shop_weapons):
                break;
            weapon = shop_weapons[stock_number];
            shop.add_field(name=weapon.icon+' '+weapon.name,value=util.format_number(weapon.price,full_precision=True,money=True));
        
        shop.set_footer(text=footer);
        
        await util.say(ctx.channel,embed=shop);
    else:
        weapon = game.Weapons.get_weapon_for_server(ctx.server.id,page);
        if weapon == None:
            raise util.DueUtilException(ctx.channel,"Weapon not found");
        weapon_info = discord.Embed(title=weapon.icon+' '+weapon.name,type="rich",color=16038978);
        weapon_info.set_thumbnail(url=weapon.image_url);
        weapon_info.add_field(name='Damage',value=util.format_number(weapon.damage));
        weapon_info.add_field(name='Accuracy',value=util.format_number(weapon.accy)+'%');
        weapon_info.add_field(name='Price',value=util.format_number(weapon.price,money=True,full_precision=True));
        weapon_info.add_field(name="Hit Message",value=weapon.hit_message);
        weapon_info.set_footer(text='Image supplied by weapon creator.');

        await util.say(ctx.channel,embed=weapon_info);
        
@commands.command(admin_only=True,args_pattern='SSCCS?S?')
async def createweapon(ctx,*args):
    
    """
    [CMD_KEY]createweapon "weapon name" "hit message" damage accy
    
    Creates a weapon for the server shop!
    
    Example usage: 
    
    [CMD_KEY]createweapon "Laser" "FIRES THEIR LAZOR AT" 100 50
    
    If you want exta customization you can also do:
    
    [CMD_KEY]createweapon "weapon name" "hit message" damage accy (image url) (melee)

    """

    weapon = game.Weapon(*args[:4],ctx=ctx);
    await util.say(ctx.channel,(weapon.icon+" **"+weapon.name.strip('*')+"** is available in the shop for "
                                +util.format_number(weapon.price,money=True)+"!"));
