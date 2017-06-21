import re
import math
import os
import random
from colour import Color
from ..game import awards
from ..configs import dueserverconfig
from ..game import game
from ..game import players
from ..game import stats
from ..game import weapons
from botstuff import util
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

"""
Worst code in the bot.
Images very ugly throwway code.
"""

# DueUtil fonts
font = ImageFont.truetype("fonts/Due_Robo.ttf", 12)
font_big = ImageFont.truetype("fonts/Due_Robo.ttf", 18)
font_med = ImageFont.truetype("fonts/Due_Robo.ttf", 14)
font_small = ImageFont.truetype("fonts/Due_Robo.ttf", 11)
font_tiny = ImageFont.truetype("fonts/Due_Robo.ttf", 9)
font_epic = ImageFont.truetype("fonts/benfont.ttf", 12)

# Templates
level_up_template = Image.open("screens/level_up.png")
new_quest_template = Image.open("screens/new_quest.png")
awards_screen_template = Image.open("screens/awards_screen.png")
quest_info_template = Image.open("screens/stats_page_quest.png")
battle_screen_template = Image.open("screens/battle_screen.png")
award_slot = Image.open("screens/award_slot.png")
quest_row = Image.open("screens/quest_row.png")
mini_icons = Image.open("screens/mini_icons.png")
profile_parts = dict()

DUE_BLACK = (48,48,48)

traffic_lights = list(Color("red").range_to(Color("#ffbf00"),5)) + list(Color("#ffbf00").range_to(Color("green"),5))

def traffic_light(colour_scale):
    # 0 Red to 1 Green
    colour = traffic_lights[int((len(traffic_lights)-1) * colour_scale)].rgb
    return tuple((int(ci * 255) for ci in colour))

def set_opacity(image,opacity_level):
    # Opaque is 1.0, input between 0-1.0
    opacity_level = int(255*opacity_level) 
    pixel_data = list(image.getdata())
    for i,pixel in enumerate(pixel_data):
        pixel_data[i] = pixel[:3] +(opacity_level,)
    image.putdata(pixel_data)
    return image
    
def colourize(image,colours,intensity,**extras):
    image = image.copy()
    pixel_data = list(image.getdata())
    threshold = extras.get('threshold',0)
    if not isinstance(colours,list):
        colours = [colours]
    cycle_colours = extras.get('cycle_colours',image.size[0] // len(colours))
    if not isinstance(cycle_colours,list):
        cycle_colours = [cycle_colours]
    colour_index = -1
    colour = colours[colour_index]
    pixel_count = 0
    for i,pixel in enumerate(pixel_data):
        # pi = pixel item
        # ci = colour item
        if cycle_colours[0] != -1 and pixel_count % cycle_colours[colour_index % len(cycle_colours)]  == 0:
            pixel_count = 0
            colour_index+=1
            colour = colours[colour_index % len(colours)]
        if sum(pixel) > threshold:
            pixel_data[i] = tuple(int(pi * (1-intensity) + ci * intensity) for pi,ci in zip(pixel[:3],colour))+pixel[3:]
        pixel_count +=1
    image.putdata(pixel_data)
    return image
    
def paste_alpha(background,image,position):
  
    """
    A paste function that does not fuck up the background when
    pasting with an image with alpha.
    """
    r, g, b, a = image.split()
    image = Image.merge("RGB", (r, g, b))
    mask = Image.merge("L", (a,))
    background.paste(image,position, mask)
    
async def load_image_url(url,**kwargs):
    if url == None:
        return None
    do_not_compress = kwargs.get('raw',False)
    file_name = 'imagecache/' + re.sub(r'\W+', '', (url))
    if len(file_name) > 128:
        file_name = file_name[:128]
    file_name = file_name + '.jpg'
    if not do_not_compress and os.path.isfile(file_name):
        return Image.open(file_name);    
    else:
        try:
            image_data = await util.download_file(url)
            image = Image.open(image_data)
            #cache image
            image.convert('RGB').save(file_name, optimize=True, quality=20)
            return image
        except:
            if os.path.isfile(file_name):
                os.remove(file_name)
            return None
            
def resize(image,width,height):
    if(image == None):
        return None
    return image.resize((width, height), Image.ANTIALIAS);        
    
async def resize_avatar(player, server, width, height): 
    return await resize_image_url(player.get_avatar_url(server),width,height)

async def resize_image_url(url, width, height):    
    return resize(await load_image_url(url),width,height)
    
def rescale_image(image, scale):
    if(image == None):
        return None;    
    width, height = image.size
    return image.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
    
def has_dimensions(image,dimensions):
    width, height = image.size
    return width == dimensions[0] and height == dimensions[1]

async def send_image(channel,image,**kwargs):
    stats.increment_stat(stats.Stat.IMAGES_SERVED)
    kwargs["filename"] = kwargs.pop('file_name',"")
    output = BytesIO()
    image.save(output,format="PNG")
    output.seek(0)
    await util.get_client(channel.server.id).send_file(channel, fp=output,**kwargs)
    output.close()

async def level_up_screen(channel,player,cash):
    image = level_up_template.copy()
    level = math.trunc(player.level)
    try:
        avatar = await resize_avatar(player,channel.server,54,54)
        image.paste(avatar, (10, 10))
    except:
        pass
    draw = ImageDraw.Draw(image)
    draw.text((159, 18), str(level), "white", font=font_big)
    draw.text((127, 40),util.format_number(cash,money=True), "white", font=font_big)
    await send_image(channel,image,file_name="level_up.png",content=":point_up_2: **"+player.name+"** Level Up!")

async def new_quest_screen(channel,quest,player):
    image = new_quest_template.copy()
    try:
        avatar = await resize_avatar(quest,channel.server,54,54)
        image.paste(avatar, (10, 10))
    except:
       pass
    draw = ImageDraw.Draw(image)
    
    draw.text((72, 20), get_text_limit_len(draw,quest.info.task,font_med,167),"white",font=font_med)
    level_text = " LEVEL " + str(math.trunc(quest.level))
    width = draw.textsize(level_text, font=font_big)[0]
    draw.text((71, 39), get_text_limit_len(draw,quest.name,
                                           font_big,168-width) + level_text, "white", font=font_big)
    await send_image(channel,image,file_name="new_quest.png",content=":crossed_swords: **"+player.name_clean+"** New Quest!")
    
async def awards_screen(channel,player,page,**kwargs):
    for_player = kwargs.get('is_player_sender',False)
    image = awards_screen_template.copy()
     
    draw = ImageDraw.Draw(image)
    suffix = " Awards"
    page_no_string_len = 0
    if page > 0:
        page_info = ": Page "+str(page+1)
        suffix += page_info
        page_no_string_len = draw.textsize(page_info,font=font)[0]
        
    name = get_text_limit_len(draw,player.get_name_possession(),font,175-page_no_string_len)
    title= name + suffix
    draw.text((15, 17),title,"white",font=font)
    count = 0
    player_award = 0
    for player_award in range(len(player.awards) - 1 - (5 * page), -1, -1):
        image.paste(award_slot, (14, 40 + 44 * count))
        award = awards.get_award(player.awards[player_award])
        draw.text((52, 47 + 44 * count),award.name, award.get_colour(default = DUE_BLACK), font=font_med)
        draw.text((52, 61 + 44 * count),award.description,DUE_BLACK, font=font_small)
        image.paste(award.icon, (19, 45 + 44 * count))
        count += 1
        msg = ""
        if count == 5:
            if player_award != 0:
                command = "myawards"
                if not for_player:
                    command = "awards @User"
                msg = ("+ "+str(len(player.awards)-(5*(page+1)))+" More. Do "
                        +dueserverconfig.server_cmd_key(channel.server)+command
                        +" "+str(page+2)+" for the next page.")
            break
    if player_award == 0:
        msg = "That's all folks!"
    if len(player.awards) == 0:
        name = get_text_limit_len(draw,player.name,font,100)
        msg = name+" doesn't have any awards!"
    width = draw.textsize(msg, font=font_small)[0]
    draw.text(((256-width)/2, 42 + 44 * count),msg,  "white", font=font_small)
    await send_image(channel,image,file_name="awards_list.png",content=":trophy: **"+player.get_name_possession_clean()+"** Awards!")
        
    
async def quests_screen(channel,player,page):
    image = awards_screen_template.copy()
    draw = ImageDraw.Draw(image)
    suffix = " Quests"
    page_no_string_len = 0
    name = get_text_limit_len(draw,player.get_name_possession(),font,175-page_no_string_len)
    if page > 0:
        page_info = ": Page "+str(page+1)
        suffix += page_info
        page_no_string_len = draw.textsize(page_info,font=font)[0]
        
    name = get_text_limit_len(draw,player.get_name_possession(),font,175-page_no_string_len)
    title= name + suffix
    draw.text((15, 17),title,"white",font=font)
    count = 0
    row_size = quest_row.size
    quest_index = 0
    for quest_index in range(len(player.quests) - 1 - (5 * page), -1, -1):
        image.paste(quest_row, (14, 40 + 44 * count))
        quest = player.quests[quest_index]
        warning_colours = [traffic_light(danger_level) for danger_level in quest.get_threat_level(player)]
        warning_icons = colourize(mini_icons,warning_colours,0.5,cycle_colours=[10,10,11,10,11])
        paste_alpha(image,warning_icons,(14+row_size[0] - 53,row_size[1]*2-12+ 44 * count))
        level = "Level "+str(math.trunc(quest.level))
        level_width = draw.textsize(level, font=font_small)[0]+5
        quest_name = get_text_limit_len(draw,quest.name,font_med,182-level_width)
        draw.text((52, 47 + 44 * count),quest_name, DUE_BLACK, font=font_med)
        name_width = draw.textsize(quest_name, font=font_med)[0]
        draw.rectangle(((53+name_width,48 + 44*count),(50+name_width + level_width,48 + 44 * count + 11)), fill="#C5505B", outline ="#83444A")
        draw.text((53+name_width +1, 48 + 44*count),level, "white", font=font_small)
        home = "Unknown"
        quest_info = quest.info
        if quest_info != None:
            home = quest_info.home
        draw.text((52, 61 + 44 * count),get_text_limit_len(draw,home,font_small,131),DUE_BLACK, font=font_small)
        quest_avatar = await resize_avatar(quest,None, 28, 28)
        if quest_avatar != None:
            image.paste(quest_avatar, (20, 46 + 44 * count))
        quest_bubble_postion = (12,row_size[1]-2+ 44 * count)
        quest_index_text = str(quest_index+1)
        quest_index_width = draw.textsize(quest_index_text, font=font_small)[0]
        draw.rectangle((quest_bubble_postion,(quest_bubble_postion[0]+quest_index_width+5,quest_bubble_postion[1]+11)), fill="#2a52be",outline ="#a1caf1")
        draw.text((15, quest_bubble_postion[1]),quest_index_text,"white", font=font_small)
        count += 1
        if count == 5:
            if quest_index != 0:
                msg = ("+ "+str(len(player.quests)-(5*(page+1)))+" More. Do "
                        +dueserverconfig.server_cmd_key(channel.server)
                        +"myquests "+str(page+2)+" for the next page.")
            break
    if quest_index == 0:
        msg = "That's all your quests!"
    if len(player.quests) == 0:
        msg = "You don't have any quests!"
    width = draw.textsize(msg, font=font_small)[0]
    draw.text(((256-width)/2, 42 + 44 * count),msg,  "white", font=font_small)
    await send_image(channel,image,file_name="awards_list.png",content=":crossed_swords: **"+player.get_name_possession_clean()+"** Quests!")
    
async def stats_screen(channel,player):

    theme = player.theme
    
    if "fontColour" in theme:
        font_colour = theme["fontColour"]
        header_colour = font_colour
        main_colour = font_colour
        banner_colour = font_colour
        side_colour = DUE_BLACK
        exp_colour = font_colour
    else:
        header_colour = theme["headerColour"]
        main_colour = theme["mainColour"]
        banner_colour = theme["bannerColour"]
        side_colour = theme["sideColour"]
        exp_colour = theme["expColour"]
    
    image = player.background.image.copy()

    draw = ImageDraw.Draw(image)
    profile_screen = profile_parts["screens"][theme["screen"]]
    paste_alpha(image,profile_screen,(0,0))
    
    if player.banner.image == None:
        init_banners()
    banner = player.banner.image
    paste_alpha(image,banner,(91,34))
    
    # draw avatar slot
    avatar_border = profile_parts["avatarborders"][theme["avatarBorder"]]
    paste_alpha(image,avatar_border,(3,6))
     
    try:
        image.paste(await resize_avatar(player,channel.server, 80, 80), (9, 12))
    except:
        pass
     
    if player.benfont:
        name=get_text_limit_len(draw,player.name_clean.replace(u"\u2026","..."),font_epic,149)
        draw.text((96, 36),name,player.rank_colour,font=font_epic)
    else:
        name=get_text_limit_len(draw,player.name,font,149)
        draw.text((96, 36), name, player.rank_colour,font=font)
    
    profile_icons = profile_parts["icons"][theme["icons"]]
    paste_alpha(image,profile_icons,(95,112))
    
    # Draw exp bar
    next_level_exp = game.get_exp_for_next_level(player.level)
    exp_bar_width = player.exp / next_level_exp * 140
    draw.rectangle(((96,70),(240,82)), theme["expBarColour"][1])
    draw.rectangle(((97,71),(239,81)), fill=theme["expBarColour"][0])
    draw.rectangle(((98,72),(98 + exp_bar_width,80)), theme["expBarColour"][1])
    exp = "EXP: "+str(math.trunc(player.exp))+" / "+str(next_level_exp)
    width = draw.textsize(exp, font=font_tiny)[0]
    if exp_bar_width >= width + 2:
        draw.text((98 + exp_bar_width - width, 72), exp, exp_colour, font=font_tiny)
            
    level = str(math.trunc(player.level))
    attk = str(round(player.attack, 2))
    strg = str(round(player.strg, 2))
    accy = str(round(player.accy, 2))
    money = util.format_number(player.money,money=True)
    
    # Text
    draw.text((96, 49), "LEVEL " + level,banner_colour, font=font_big)
    draw.text((94, 87), "INFORMATION",header_colour, font=font_big)
    draw.text((117, 121), "ATK", main_colour, font=font)
    draw.text((117, 149), "STRG", main_colour, font=font)
    draw.text((117, 177), "ACCY", main_colour, font=font)
    draw.text((117, 204), "CASH", main_colour, font=font)
    draw.text((117, 231), "WPN", main_colour, font=font)
    draw.text((96, 252), "QUESTS BEAT", main_colour, font=font)
    draw.text((96, 267), "WAGERS WON", main_colour, font=font)
    
    # Player stats
    width = draw.textsize(attk, font=font)[0]
    draw.text((241 - width, 122), attk, main_colour, font=font)
    width = draw.textsize(strg, font=font)[0]
    draw.text((241 - width, 150), strg, main_colour, font=font)
    width = draw.textsize(accy, font=font)[0]
    draw.text((241 - width, 178), accy, main_colour, font=font)
    width = draw.textsize(money, font=font)[0]
    draw.text((241 - width, 204),money, main_colour, font=font)
    width= draw.textsize(str(player.quests_won), font=font)[0]
    draw.text((241 - width, 253), str(player.quests_won), main_colour, font=font)
    width = draw.textsize(str(player.wagers_won), font=font)[0]
    draw.text((241 - width, 267), str(player.wagers_won), main_colour, font=font)
    wep = get_text_limit_len(draw,player.weapon.name,font,95)
    width = draw.textsize(wep, font=font)[0]
    draw.text((241 - width, 232), wep, main_colour, font=font)
        
    # Player awards
    count = 0
    row = 0
    for player_award in range(len(player.awards) - 1, -1, -1):
         if count % 2 == 0:
             image.paste(awards.get_award(player.awards[player_award]).icon, (18, 121 + 35 * row))
         else:
             image.paste(awards.get_award(player.awards[player_award]).icon, (53, 121 + 35 * row))
             row +=1
         count += 1
         if count == 8:
             break
             
    if len(player.awards) > 8:
        draw.text((18, 267), "+ " + str(len(player.awards) - 8) + " More", side_colour, font=font)
    elif len(player.awards) == 0:
        draw.text((38, 183), "None", side_colour, font=font)

    await send_image(channel,image,file_name="myinfo.png",content=":pen_fountain: **"+player.get_name_possession_clean()+"** information."); 
       
async def quest_screen(channel,quest):

    image = quest_info_template.copy()
        
    try:
        image.paste(await resize_avatar(quest,None, 72, 72), (9, 12))
    except:
        pass
        
    level = str(math.trunc(quest.level))
    attk = str(round(quest.attack, 2))
    strg = str(round(quest.strg, 2))
    accy = str(round(quest.accy, 2))
    reward = util.format_number(quest.money,money=True)

    draw = ImageDraw.Draw(image)
    name = get_text_limit_len(draw,quest.name,font,114)
    quest_info = quest.info
    draw.text((88, 38), name, quest.rank_colour, font=font)
    draw.text((134, 58), " " + str(level), "white", font=font_big)
   
    # Fill data
    width = draw.textsize(attk, font=font)[0]
    draw.text((203 - width, 123), attk, "white", font=font)
    width= draw.textsize(strg, font=font)[0]
    draw.text((203 - width, 151), strg, "white", font=font)
    width = draw.textsize(accy, font=font)[0]
    draw.text((203 - width, 178), accy, "white", font=font)
    weapon_name = get_text_limit_len(draw,quest.weapon.name,font,136)
    width = draw.textsize(weapon_name, font=font)[0]
    draw.text((203 - width, 207), weapon_name, "white", font=font)
    
    if quest_info != None:
        creator = get_text_limit_len(draw,quest_info.creator,font,119)
        home = get_text_limit_len(draw,quest_info.home,font,146)
    else:
        creator = "Unknown"
        home = "Unknown"
    
    width = draw.textsize(creator, font=font)[0]
    draw.text((203 - width, 228), creator, "white", font=font)
    width = draw.textsize(home, font=font)[0]
    draw.text((203 - width, 242), home, "white", font=font)
    width = draw.textsize(reward, font=font_med)[0]
    draw.text((203 - width, 266),reward, DUE_BLACK, font=font_med)

    await send_image(channel,image,file_name="questinfo.png",content=":pen_fountain: Here you go."); 

    
async def battle_screen(channel,player_one,player_two):

    image = battle_screen_template.copy()
    width, height = image.size
        
    try:
        image.paste(await resize_avatar(player_one,channel.server, 54, 54), (9, 9))
    except:
        pass
        
    try:
        image.paste(await resize_avatar(player_two,channel.server, 54, 54),  (width - 9 - 55, 9))
    except:
        pass
        
    weapon_one = player_one.weapon
    weapon_two = player_two.weapon
        
    wep_image_one = await resize_image_url(weapon_one.image_url, 30, 30)
    
    if wep_image_one == None:
        wep_image_one = await resize_image_url(weapons.NO_WEAPON.image_url, 30, 30)
		
    try:
        image.paste(wep_image_one, (6, height - 6 - 30), wep_image_one)
    except:
        image.paste(wep_image_one, (6, height - 6 - 30))
        
    wep_image_two = await resize_image_url(weapon_two.image_url, 30, 30)
    
    if wep_image_two == None:
        wep_image_two = await resize_image_url(weapons.NO_WEAPON.image_url, 30, 30)
    try:
        image.paste(wep_image_two, (width - 30 - 6, height - 6 - 30), wep_image_two)
    except:
        image.paste(wep_image_two, (width - 30 - 6, height - 6 - 30))
        
    draw = ImageDraw.Draw(image)
    draw.text((7, 64), "LEVEL " + str(math.trunc(player_one.level)), "white", font=font_small)
    draw.text((190, 64), "LEVEL " + str(math.trunc(player_two.level)), "white", font=font_small)
    weap_one_name = get_text_limit_len(draw,weapon_one.name,font,85)
    width = draw.textsize(weap_one_name, font=font)[0]
    draw.text((124 - width, 88), weap_one_name, "white", font=font)
    draw.text((132, 103), get_text_limit_len(draw,weapon_two.name,font,85), "white", font=font)
   
    await send_image(channel,image,file_name="battle.png"); 
    
async def googly_eyes(channel,eye_type):

    
    """
    Googly eye generator.
    
    WARNING: I messed up! eye_type could mean eye_postion or eye_type (pos + buch of mods)
    Depending on context
    """
    
    eye_types = ("derp","left","right","center","bottom","top","centre")

    def strip_modifier(eye_type,modifer):
        return eye_type.replace(modifer,"").strip()
        
    def random_eyes():
        
        """
        Returns a random eye postion
        """
        
        nonlocal eye_types
        return random.choice(eye_types)
        
    def random_eye_type():
      
        """
        A random eye type pos + mods
        """
        nonlocal eye_types
        mods = ["evil","gay","snek","high","ogre","emoji","small"]
        eye_type = ""
        for number_of_mods in range(0,random.randrange(0,len(mods))):
            mod = random.choice(mods)
            eye_type += mod
            mods.remove(mod)
        return eye_type+random_eyes()
        
    if eye_type == "":
        eye_type = random_eye_type()

    size = (300*2,300*2)
    border_scale = 1
    pupil_scale = 1
    high_scale = 1
    if "small" in eye_type:
        eye_type = strip_modifier(eye_type,"small")    
        size = (150*2,150*2)
        border_scale = 1.5
        pupil_scale = 1.5
        high_scale = 0.7
    if "emoji" in eye_type:
        eye_type = strip_modifier(eye_type,"emoji")    
        size = (32*2,32*2)
        border_scale = 0
        pupil_scale = 2.3
        high_scale = 0.6
    width,height = size
    size = (size[0]+5,size[1]+5)
    image = Image.new("RGBA",size)
    draw = ImageDraw.Draw(image)

    def draw_eye(x,y):
        nonlocal size,draw,width,height,eye_types,border_scale,pupil_scale,high_scale,eye_type
        pupil_colour = "black"
        border_colour = "black"
        eye_colour = "white"
        given_eye_type = eye_type
        if "evil" in given_eye_type:
            pupil_colour = "red"
            given_eye_type = strip_modifier(given_eye_type,"evil")
        if "gay" in given_eye_type:
            border_colour = "#ff0280"
            given_eye_type = strip_modifier(given_eye_type,"gay")
        if "high" in given_eye_type:
            given_eye_type = strip_modifier(given_eye_type,"high")
            pupil_width = int(width//5*high_scale)
            pupil_height = int(height//4*high_scale)
            eye_colour = "#ffb5b5"
        else:
            pupil_width = width//10
            pupil_height = height//8
        if "ogre" in given_eye_type:
            given_eye_type = strip_modifier(given_eye_type,"ogre")
            pupil_colour = "#ffb22d"
            eye_colour = "#bef9a4"
        if "snek" in given_eye_type:
            given_eye_type = strip_modifier(given_eye_type,"snek")
            pupil_width = int(pupil_width * 0.4)
            pupil_height = int(pupil_height * 1.8)
            
        pupil_width = int(pupil_width * pupil_scale)
        pupil_height = int(pupil_height *pupil_scale)
        
        draw.ellipse([x,y,x+width//2,height],fill=border_colour)
        border_width = int(width//20*border_scale)
        draw.ellipse([x+border_width,y+border_width,x+width//2-border_width,height-border_width],fill=eye_colour)
        inner_width = width//2-2*border_width 
        inner_height = height-y-2*border_width
        pupil_x_centre = x + (width//2 - pupil_width)//2
        pupil_y_centre = (height - pupil_height)//2
        
        shift_x = min(inner_width//4,(width -pupil_width)//2)
        shift_y = min(inner_height//4,(height -pupil_height)//2)

        if not any(direction in given_eye_type for direction in ("left","right","top","bottom","centre","center")):
            given_eye_type = random_eyes()
            eye_type = eye_type.replace(given_eye_type," ") + given_eye_type
        if given_eye_type == "derp":
            pupli_x_limit_1 = border_width+pupil_width+pupil_x_centre-inner_width//2
            pupli_x_limit_2 = pupil_x_centre-border_width-pupil_width+inner_width//2
            pupil_x = random.randrange(min(pupli_x_limit_1,pupli_x_limit_2),max(pupli_x_limit_1,pupli_x_limit_2))
            pupli_y_limit_1 = border_width+pupil_height+pupil_y_centre-inner_height//2
            pupli_y_limit_2 = pupil_y_centre-border_width-pupil_height+inner_height//2
            pupil_y = random.randrange(min(pupli_y_limit_1,pupli_y_limit_2),max(pupli_y_limit_1,pupli_y_limit_2))
        else:
            pupil_x = pupil_x_centre
            pupil_y = pupil_y_centre
            if "left" in given_eye_type:
                pupil_x -= shift_x
            if "right" in given_eye_type:
                pupil_x += shift_x
            if "top" in given_eye_type:
                pupil_y -= shift_y
            if "bottom" in given_eye_type:
                pupil_y += shift_y
        draw.ellipse([pupil_x,pupil_y,pupil_x+pupil_width,pupil_y+pupil_height],fill=pupil_colour)
    draw_eye(0,0)
    draw_eye(size[0]//2,0)
    image = resize(image,width//2,height//2)
    await send_image(channel,image,file_name="eyes.png")

def get_text_limit_len(draw,text,given_font,length):
    removed_chars = False
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    for x in range(0, len(text)):
        width = draw.textsize(text, font=given_font)[0]
        if(width > length):
            text = text[:len(text)-1]
            removed_chars = True
        else:
            if removed_chars:
                if (given_font != font_epic):
                    return text[:-1] + u"\u2026"
                else:
                    return text[:-3] + "..."
            return text

def load_profile_parts():
    global profile_parts
    profile_parts["icons"] = dict()
    profile_parts["avatarborders"] = dict()
    profile_parts["screens"] = dict()
    for path, subdirs, files in os.walk("screens/profiles/"):
        for name in files:
            if name.endswith(".png"):
                file_path = os.path.join(path, name)
                part_type = path.rsplit("/",1)[-1]
                name = name.replace('.png','')
                profile_parts[part_type][name] = Image.open(file_path) 
   
def init_banners():
    for banner in players.banners.values():
        if banner.image == None:
            banner.image = set_opacity(Image.open('screens/info_banners/'+banner.image_name),0.9)
            
init_banners()
load_profile_parts()
