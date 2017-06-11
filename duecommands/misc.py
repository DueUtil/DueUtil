from botstuff import commands
from botstuff import util
from botstuff.permissions import Permission
from fun import misc,imagehelper,players,awards
import re
import json
import os

async def glitter_text(channel,text):
    gif_text = misc.get_glitter_text(text)
    await util.get_client(channel).send_file(channel, fp=gif_text,
                                             filename="glittertext.gif", 
                                             content=":sparkles: Your glitter text!")

@commands.command(permission = Permission.DUEUTIL_ADMIN,args_pattern="S")
@commands.imagecommand()
async def glittertext(ctx,*args,**details): 
    await glitter_text(ctx.channel,args[0])

@commands.command()
async def wish(ctx,*args,**details): 
    player = details["author"]
    player.quest_spawn_build_up += 0.000000001
    
@commands.command(permission = Permission.DUEUTIL_MOD,args_pattern="SSSSIP?")
async def uploadbg(ctx,*args,**details): 
  
    """
    
    [CMD_KEY]uploadbg (a bunch of args)
    
    Takes:
      icon
      name
      desc
      url
      price
      
    in that order.
    
    NOTE: Make event/shitty backgrounds (xmas) etc **free** (so we can delete them)
    
    """
    
    submitter = None
    if len(args) == 6:
        submitter = args[5]
    
    icon = args[0]
    if not util.char_is_emoji(icon): 
        raise util.DueUtilException(ctx.channel,"Icon must be emoji!")
    description = args[2]
    price = args[4]
    
    name = util.filter_string(args[1])
    if name != args[1]:
        raise util.DueUtilException(ctx.channel,"Invalid background name!")
    name = re.sub(' +',' ',name)
    
    if name.lower() in players.backgrounds:
        raise util.DueUtilException(ctx.channel,"That background name has already been used!")
      
    if price < 0:
        raise util.DueUtilException(ctx.channel,"Cannot have a negative background price!")
      
    url = args[3]
    image = imagehelper.load_image_url(url,raw=True)
    if image == None:
        raise util.DueUtilException(ctx.channel,"Failed to load image!")
        
    if not imagehelper.has_dimensions(image,(256,299)):
        raise util.DueUtilException(ctx.channel,"Image must be ``256*299``!")
        
    image_name = name.lower().replace(' ','_')+".png"
    image.save('backgrounds/'+image_name)
    
    with open('backgrounds/backgrounds.json', 'r+') as backgrounds_file:
        backgrounds = json.load(backgrounds_file)
        backgrounds[name.lower()] = {"name":name,"icon":icon,"description":description,"image":image_name,"price":price}
        backgrounds_file.seek(0)
        backgrounds_file.truncate()
        json.dump(backgrounds, backgrounds_file, indent=4)
        
    players.backgrounds.load_backgrounds()
    
    await util.say(ctx.channel,":white_check_mark: Background **"+name+"** has been uploaded!")
    if submitter != None:
        await awards.give_award(ctx.channel, submitter, "BgAccepted", "Background Accepted!")

@commands.command(permission = Permission.DUEUTIL_MOD,args_pattern="S")
async def testbg(ctx,*args,**details): 
  
    """
    [CMD_KEY]testbg (image url)

    Tests if a background is the correct dimensions.
    
    """
    
    url = args[0]
    image = imagehelper.load_image_url(url)
    if image == None:
        raise util.DueUtilException(ctx.channel,"Failed to load image!")
    
    if not imagehelper.has_dimensions(image,(256,299)):
        width,height = image.size
        await util.say(ctx.channel,(":thumbsdown: **That does not meet the requirements!**\n"
                                    +"The tested image had the dimensions ``"+str(width)+"*"+str(height)+"``!\n"
                                    +"It should be ``256*299``!"))
    else:
        await util.say(ctx.channel,(":thumbsup: **That looks good to me!**\n"
                                   +"P.s. I can't check for low quality images!"))

    
@commands.command(permission = Permission.DUEUTIL_MOD,args_pattern="S")
async def deletebg(ctx,*args,**details): 
  
    """
    [CMD_KEY]deletebg (background name)
    
    Deletes a background.
    
    DO NOT DO THIS UNLESS THE BACKGROUND IS FREE
    
    """
    
    background_to_delete = args[0].lower()
    
    if not background_to_delete in players.backgrounds:
        raise util.DueUtilException(ctx.channel,"Background not found!")
    if background_to_delete == "default":
        raise util.DueUtilException(ctx.channel,"Can't delete default background!")
    background = players.backgrounds[background_to_delete]
    
    with open('backgrounds/backgrounds.json', 'r+') as backgrounds_file:
        backgrounds = json.load(backgrounds_file)
        del backgrounds[background_to_delete]
        backgrounds_file.seek(0)
        backgrounds_file.truncate()
        json.dump(backgrounds, backgrounds_file, indent=4)
    os.remove("backgrounds/"+background["image"]);

    players.backgrounds.load_backgrounds()
        
    await util.say(ctx.channel,":wastebasket: Background **"+background.name_clean+"** has been deleted!")
