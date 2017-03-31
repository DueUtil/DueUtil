import re
import requests
import math
import os
import io
from fun import players, stats
from botstuff import util
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# DueUtil fonts
font = ImageFont.truetype("fonts/Due_Robo.ttf", 12)
font_big = ImageFont.truetype("fonts/Due_Robo.ttf", 18)
font_med = ImageFont.truetype("fonts/Due_Robo.ttf", 14)
font_small = ImageFont.truetype("fonts/Due_Robo.ttf", 11)
font_epic = ImageFont.truetype("fonts/benfont.ttf", 12)

# Templates
info_avatar = Image.open("screens/info_avatar.png")
level_up_template = Image.open("screens/level_up.png")
new_quest_template = Image.open("screens/new_quest.png")
awards_screen_template = Image.open("screens/awards_screen.png")
stats_screen_template = Image.open("screens/info_screen.png")
quest_info_template = Image.open("screens/stats_page_quest.png")
battle_screen_template = Image.open("screens/battle_screen.png")
award_slot = Image.open("screens/award_slot.png")

def set_opacity(image,opacity_level):
    # Opaque is 1.0, input between 0-1.0
    opacity_level = int(255*opacity_level) 
    pixel_data = list(image.getdata())
    for i,pixel in enumerate(pixel_data):
        pixel_data[i] = pixel[:3] +(opacity_level,)
    image.putdata(pixel_data)
    return image
        
def load_image_url(url,**kwargs):
    do_not_compress = kwargs.get('raw',False)
    file_name = 'imagecache/' + re.sub(r'\W+', '', (url))
    if len(file_name) > 128:
        file_name = file_name[:128]
    file_name = file_name + '.jpg'
    if not do_not_compress and os.path.isfile(file_name):
        return Image.open(file_name);    
    else:
        try:
            response = requests.get(url, timeout=10)
            if 'image' not in response.headers.get('content-type'):
                return None
            image_date = io.BytesIO(response.content)
            image = Image.open(image_date)
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
    
def resize_avatar(player, server, width, height): 
    return resize_image_url(player.get_avatar_url(server),width,height)

def resize_image_url(url, width, height):    
    return resize(load_image_url(url),width,height)
    
def rescale_image(image, scale):
    if(image == None):
        return None;    
    width, height = image.size
    return image.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
    
async def send_image(channel,image,**kwargs):
    stats.increment_stat(stats.Stat.IMAGES_SERVED)
    content = kwargs.get('content',"")
    file_name = kwargs.get('file_name',"")
    output = BytesIO()
    image.save(output,format="PNG")
    output.seek(0)
    await util.get_client(channel.server.id).send_file(channel, fp=output, filename=file_name,content=content)
    output.close()

async def level_up_screen(channel,player,cash):
    image = level_up_template.copy()
    level = math.trunc(player.level)
    try:
        avatar = resize_avatar(player,channel.server,54,54)
        image.paste(avatar, (10, 10))
    except:
        pass
    draw = ImageDraw.Draw(image)
    draw.text((159, 18), str(level), (255, 255, 255), font=font_big)
    draw.text((127, 40),util.format_number(cash,money=True), (255, 255, 255), font=font_big)
    await send_image(channel,image,file_name="level_up.png",content=":point_up_2: **"+player.name+"** Level Up!")

async def new_quest_screen(channel,quest,player):
    image = new_quest_template.copy()
    try:
        avatar = resize_avatar(quest,channel.server,54,54)
        image.paste(avatar, (10, 10))
    except:
       pass
    draw = ImageDraw.Draw(image)
    
    draw.text((72, 20), get_text_limit_len(draw,util.clear_markdown_escapes(quest.info.task),font_med,167), 
                                           (255, 255, 255), font=font_med)
    level_text = " LEVEL " + str(math.trunc(quest.level))
    width = draw.textsize(level_text, font=font_big)[0]
    
    draw.text((71, 39), get_text_limit_len(draw,util.clear_markdown_escapes(g_quest.monsterName),
                                           font_big,168-width) + level_text, (255, 255, 255), font=font_big)
    await send_image(channel,image,file_name="new_quest.png",content=":crossed_swords: **"+player.name+"** New Quest!")
    
async def awards_screen(channel,player,page,**kwargs):
    for_player = kwargs.get('is_player_sender',False)
    image = awards_screen_template.copy()
     
    draw = ImageDraw.Draw(image)
    suffix = "'s Awards"
    page_no_string_len = 0
    if(page > 0):
        page_info = ": Page "+str(page+1)
        suffix += page_info
        page_no_string_len = draw.textsize(page_info,font=font)[0]
        
    name = get_text_limit_len(draw,player.name,font,175-page_no_string_len); 
    title=name+suffix
        
    draw.text((15, 17),title,(255,255,255),font=font)
    
    count = 0
    player_award = 0
    for player_award in range(len(player.awards) - 1 - (5 * page), -1, -1):
         image.paste(award_slot, (14, 40 + 44 * count))
         award = game.Award.get_award(player.awards[player_award])
         draw.text((52, 47 + 44 * count),award.name, (48, 48, 48), font=font_med)
         draw.text((52, 61 + 44 * count),award.description,(48, 48, 48), font=font_small)
         image.paste(award.icon, (19, 45 + 44 * count))
         count += 1
         msg = ""
         if count == 5:
             if player_award != 0:
                 command = "myawards"
                 if not for_player:
                     command = "awards @User"
                 msg = "+ "+str(len(player.awards)-(5*(page+1)))+" More. Do "+util.get_server_cmd_key(channel.server)+command+" "+str(page+2)+" for the next page."
             break
    if player_award == 0:
        msg = "That's all folks!"
    if len(player.awards) == 0:
        name = get_text_limit_len(draw,player.name,font,100)
        msg = name+" doesn't have any awards!"
    width = draw.textsize(msg, font=font_small)[0]
    draw.text(((256-width)/2, 42 + 44 * count),msg,  (255, 255, 255), font=font_small)
    
    await send_image(channel,image,file_name="awards_list.png",content=":trophy: **"+player.name+"'s** Awards!")

async def stats_screen(channel,player):

    try:
        image = Image.open("backgrounds/" + player.background)
    except:
        image = Image.open("backgrounds/default.png")

    draw = ImageDraw.Draw(image)
    image.paste(stats_screen_template,(0,0),stats_screen_template)
    
    if player.banner.image == None:
        init_banners()
    banner = player.banner.image
    
    image.paste(banner,(91,34),banner)
    
    # draw avatar slot
    image.paste(info_avatar,(3,6),info_avatar)
     
    try:
        image.paste(resize_avatar(player,channel.server, 80, 80), (9, 12))
    except:
        pass
     
    if player.benfont:
        name=get_text_limit_len(draw,player.clean_name.replace(u"\u2026","..."),font_epic,149)
        draw.text((96, 42),name,player.rank_colour,font=font_epic)
    else:
        name=get_text_limit_len(draw,player.name,font,149)
        draw.text((96, 42), name, player.rank_colour,font=font)
            
    level = str(math.trunc(player.level))
    attk = str(round(player.attack, 2))
    strg = str(round(player.strg, 2))
    accy = str(round(player.accy, 2))
    money = str(util.format_number(player.money,money=True))
    
    # Fill data
    
    draw.text((96, 62), "LEVEL " + level, (255, 255, 255), font=font_big)
        
    width = draw.textsize(attk, font=font)[0]
    draw.text((241 - width, 122), attk, (255, 255, 255), font=font)

    width = draw.textsize(strg, font=font)[0]
    draw.text((241 - width, 150), strg, (255, 255, 255), font=font)

    width = draw.textsize(accy, font=font)[0]
    draw.text((241 - width, 178), accy, (255, 255, 255), font=font)

    width = draw.textsize(money, font=font)[0]
    draw.text((241 - width, 204),money, (255, 255, 255), font=font)
    
    width= draw.textsize(str(player.quests_won), font=font)[0]
    draw.text((241 - width, 253), str(player.quests_won), (255, 255, 255), font=font)
    
    width = draw.textsize(str(player.wagers_won), font=font)[0]
    draw.text((241 - width, 267), str(player.wagers_won), (255, 255, 255), font=font)
    
    wep = get_text_limit_len(draw,player.weapon.name,font,95)
    width = draw.textsize(wep, font=font)[0]
    draw.text((241 - width, 232), wep, (255, 255, 255), font=font)
        
    count = 0
    row = 0
    first_even = True
    for player_award in range(len(player.awards) - 1, -1, -1):
         if count % 2 == 0:
             image.paste(game.Award.get_award(player.awards[player_award]).icon, (18, 121 + 35 * row))
         else:
             image.paste(game.Award.get_award(player.awards[player_award]).icon, (53, 121 + 35 * row))
             row +=1
         count += 1
         if count == 8:
             break
             
    if len(player.awards) > 8:
        draw.text((18, 267), "+ " + str(len(player.awards) - 8) + " More", (48, 48, 48), font=font)
    elif len(player.awards) == 0:
        draw.text((38, 183), "None", (48, 48, 48), font=font)

    await send_image(channel,image,file_name="myinfo.png",content=":pen_fountain: **"+player.name+"'s** information."); 
       
async def quest_screen(channel,quest):

    image = quest_info_template.copy()
        
    try:
        image.paste(resize_avatar(quest,channel.server, 72, 72), (9, 12))
    except:
        pass
        
    level = str(math.trunc(quest.level))
    attk = str(round(quest.attack, 2))
    strg = str(round(quest.strg, 2))
    accy = str(round(quest.accy, 2))
    reward = util.number_format(quest.money,money=True)

    draw = ImageDraw.Draw(image)
    name = get_text_limit_len(draw,util.clear_markdown_escapes(quest.name),font,114)
    
    quest_info = quest.info
    draw.text((88, 38), name, quest.rank_colour, font=font)
    draw.text((134, 58), " " + str(level), (255, 255, 255), font=font_big)
   
    # Fill data
    width = draw.textsize(attk, font=font)[0]
    draw.text((203 - width, 123), attk, (255, 255, 255), font=font)

    width= draw.textsize(strg, font=font)[0]
    draw.text((203 - width, 151), strg, (255, 255, 255), font=font)

    width = draw.textsize(accy, font=font)[0]
    draw.text((203 - width, 178), accy, (255, 255, 255), font=font)

    weapon_name = get_text_limit_len(draw,quest.weapon.name,font,136)
    width = draw.textsize(weapon_name, font=font)[0]
    draw.text((203 - width, 207), weapon_name, (255, 255, 255), font=font)
    
    if quest_info != None:
        creator = get_text_limit_len(draw,quest.creator.name,font,119)
        home = get_text_limit_len(draw,str(quest_info.home),font,146)
    else:
        creator = "Unknown"
        home = "Unknown"
    
    width = draw.textsize(creator, font=font)[0]
    draw.text((203 - width, 228), creator, (255, 255, 255), font=font)
    
    width = draw.textsize(home, font=font)[0]
    draw.text((203 - width, 242), home, (255, 255, 255), font=font)
    
    width = draw.textsize(reward, font=font_med)[0]
    draw.text((203 - width, 266),reward, (48, 48, 48), font=font_med)

    await send_image(channel,image,file_name="questinfo.png",content=":pen_fountain: Here you go."); 

    
async def battle_screen(channel,player_one,player_two,battle_text):

    image = battle_screen_template.copy()
    width, height = image.size
        
    try:
        image.paste(resize_avatar(player_one,channel.server, 54, 54), (9, 9))
    except:
        pass
        
    try:
        image.paste(resize_avatar(player_two,channel.server, 54, 54),  (width - 9 - 55, 9))
    except:
        pass
        
    weapon_one = player_one.weapon
    weapon_two = player_two.weapon
   
    if(avatar_one != None):
        img.paste(avatar_one, (9, 9))
    if(avatar_two != None):
        img.paste(avatar_two, (width - 9 - 55, 9))
        
    wep_image_one = resize_image_url(weapon_one.image_url, 30, 30)
    
    if(wep_image_one == None):
        wep_image_one = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30)
		
    try:
        img.paste(wep_image_one, (6, height - 6 - 30), wep_image_one)
    except:
        img.paste(wep_image_one, (6, height - 6 - 30))
        
    wep_image_two = resize_image_url(weapon_two.image_url, 30, 30)
    
    if(wep_image_two == None):
        wep_image_two = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30)
    try:
        img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30), wep_image_two)
    except:
        img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30))
        
    draw = ImageDraw.Draw(img)
    draw.text((7, 64), "LEVEL " + str(math.trunc(pone.level)), (255, 255, 255), font=font_small)
    draw.text((190, 64), "LEVEL " + str(math.trunc(ptwo.level)), (255, 255, 255), font=font_small)
    weap_one_name = get_text_limit_len(draw,util.clear_markdown_escapes(weapon_one.name),font,85)
    width = draw.textsize(weap_one_name, font=font)[0]
    draw.text((124 - width, 88), weap_one_name, (255, 255, 255), font=font)
    draw.text((132, 103), get_text_limit_len(draw,util.clear_markdown_escapes(weapon_two.name),font,85), (255, 255, 255), font=font)
   
    await send_image(channel,image,file_name="battle.png"); 
    

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

def init_banners():
    for banner in players.banners.values():
        if banner.image == None:
            banner.image = set_opacity(Image.open('screens/info_banners/'+banner.image_name),0.9)

init_banners()
