

def set_opacity(image,opacity_level):
    opacity_level = int(255*opacity_level) 
    # Opaque is 255, input between 0-255
    pixel_data = list(image.getdata())
    for i,pixel in enumerate(pixel_data):
        pixel_data[i] = pixel[:3] +(opacity_level,);
    image.putdata(pixeldata)
    return image
    
    
def load_image_url(url,**kwargs):
    do_not_compress = kwargs.get('raw',False);
    file_name = 'imagecache/' + re.sub(r'\W+', '', (url));
    if len(file_name) > 128:
        file_name = file_name[:128];
    file_name = file_name + '.jpg';
    if not do_not_compress and os.path.isfile(fname):
        return Image.open(fname);    
    else:
        try:
            response = requests.get(url, timeout=10)
            if 'image' not in response.headers.get('content-type'):
                return None;
            image_file = io.BytesIO(response.content);
            img = Image.open(image_file);
            #cache image
            img.convert('RGB').save(file_name, optimize=True, quality=20);
            return img;
        except:
            if os.path.isfile(file_name):
                os.remove(file_name);
            return None;
            
def resize_avatar(player, server, q, w, h):    
    if(not q):
        u = server.get_member(player.userid);
        if(u.avatar_url != ""):
            img = loadImageFromURL(u.avatar_url);
        else:
            img = loadImageFromURL(u.default_avatar_url);
    else:
        img = loadImageFromURL(get_game_quest_from_id(player.qID).image_url);
        if(img == None):
            return None;
    img = img.resize((w, h), Image.ANTIALIAS);
    return img;

def resize_image_url(url, w, h):    
    img = loadImageFromURL(url);
    if(img == None):
        return None;
    img = img.resize((w, h), Image.ANTIALIAS);
    return img;
    
def rescale_image(path, scale):    
    img = Image.open(path);
    width, height = img.size;
    if(img == None):
        return None;
    img = img.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS);
    return img;

async def level_up_image(message, player, cash):
    global images_served;
    images_served = images_served +1;
    level = math.trunc(player.level);
    try:
        avatar = resize_avatar(player, message.server, False, 54, 54);
    except:
        avatar = None;
    img = Image.open("screens/level_up.png");
    if(avatar != None):
        img.paste(avatar, (10, 10));
    draw = ImageDraw.Draw(img)
    draw.text((159, 18), str(level), (255, 255, 255), font=font_big)
    draw.text((127, 40), "$" + util.to_money(cash,True), (255, 255, 255), font=font_big)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="level_up.png",content=":point_up_2: **"+player.name+"** Level Up!");
    output.close()


async def new_quest_image(message, quest, player):
    global images_served;
    images_served = images_served +1;
    try:
        avatar = resize_avatar(quest, message.server, True, 54, 54);
    except:
        avatar = None;
    img = Image.open("screens/new_quest.png"); 
    if(avatar != None):
        img.paste(avatar, (10, 10));
    draw = ImageDraw.Draw(img)
    g_quest = get_game_quest_from_id(quest.qID);
    draw.text((72, 20), get_text_limit_len(draw,util.clear_markdown_escapes(g_quest.quest),font_med,167), (255, 255, 255), font=font_med)
    level_text = " LEVEL " + str(math.trunc(quest.level));
    width = draw.textsize(level_text, font=font_big)[0]
    draw.text((71, 39), get_text_limit_len(draw,util.clear_markdown_escapes(g_quest.monsterName),font_big,168-width) + level_text, (255, 255, 255), font=font_big)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="new_quest.png",content=":crossed_swords: **"+player.name+"** New Quest!");
    output.close()                

async def awards_screen(message, player,page):
    global images_served;
    images_served = images_served +1;
    sender = findPlayer(message.author.id);
    if(time.time() - sender.last_image_request < 10):
        await get_client(message.server.id).send_message(message.channel,":cold_sweat: Please don't break me!");
        return;
    sender.last_image_request = time.time();
    #player.last_image_request = time.time();
    await get_client(message.server.id).send_typing(message.channel);
    img = Image.open("screens/awards_screen.png"); 
    a_s = Image.open("screens/award_slot.png"); 
    draw = ImageDraw.Draw(img)
    t = "'s Awards";
    pageInfoLen = 0;
    if(page > 0):
        pageInfo = ": Page "+str(page+1);
        t += pageInfo;
        pageInfoLen = draw.textsize(pageInfo, font=font)[0]
    name = get_text_limit_len(draw,util.clear_markdown_escapes(player.name),font,175-pageInfoLen); 
    t=name+t;
        
    draw.text((15, 17), t,(255,255,255), font=font)
    c = 0;
    l = 0;
    x = 0;
    for x in range(len(player.awards) - 1 - (5*page), -1, -1):
         img.paste(a_s, (14, 40 + 44 * c));
         draw.text((52, 47 + 44 * c), AwardsNames[player.awards[x]].split("\n")[0],  (48, 48, 48), font=font_med)
         draw.text((52, 61 + 44 * c), AwardsNames[player.awards[x]].split("\n")[1],  (48, 48, 48), font=font_small)
         img.paste(AwardsIcons[player.awards[x]], (19, 45 + 44 * c));
         c = c + 1;
         msg = "";
         if(c == 5):
             if(x != 0):
                 a = "myawards";
                 if(message.content.lower().startswith(util.get_server_cmd_key(message.server)+"awards")):
                     a = "awards @User";
                 msg = "+ "+str(len(player.awards)-(5*(page+1)))+" More. Do "+filter_func(util.get_server_cmd_key(message.server))+a+" "+str(page+2)+" for the next page.";
             break;
    if (x == 0):
        msg = "That's all folks!"
    if (len(player.awards) == 0):
        name = get_text_limit_len(draw,util.clear_markdown_escapes(player.name),font,100);
        msg = name+" doesn't have any awards!";
    width = draw.textsize(msg, font=font_small)[0]
    draw.text(((256-width)/2, 42 + 44 * c),msg,  (255, 255, 255), font=font_small)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="awards_list.png",content=":trophy: **"+player.name+"'s** Awards!");
    output.close()
        

async def display_stats_image(player, q, message):
    global images_served;
    images_served = images_served +1;
    sender = Player.find_player(message.author.id);
    print(players);
    if(time.time() - sender.last_image_request < 10):
        await util.say(message.channel,":cold_sweat: Please don't break me!");
        return;
    sender.last_image_request = time.time();
    
    await util.get_client(message.server.id).send_typing(message.channel);
    if(q):
        await displayQuestImage(player, message);
        return;
    try:
        avatar = resize_avatar(player, message.server, q, 80, 80);
    except:
        avatar = None;
    
    level = math.trunc(player.level);
    attk = round(player.attack, 2);
    strg = round(player.strg, 2);
    shooting = round(player.accy, 2)
    name = util.clear_markdown_escapes(player.name);
    try:
        img = Image.open("backgrounds/" + player.background);
    except:
        img = Image.open("backgrounds/default.png");
        
    screen = Image.open("screens/info_screen.png");   
    
    draw = ImageDraw.Draw(img);
    img.paste(screen,(0,0),screen)
    
    #draw_banner
    #player_banner = get_player_banner(player);
    
    #img.paste(player_banner,(91,34),player_banner);
    
    #draw_avatar slot
    img.paste(info_avatar,(3,6),info_avatar);
     
    if(player.benfont):
        name=get_text_limit_len(draw,filter_func(name.replace(u"\u2026","...")),font_epic,149)
        draw.text((96, 42),name, get_rank_colour(int(level / 10) + 1), font=font_epic)
    else:
        name=get_text_limit_len(draw,name,font,149)
        draw.text((96, 42), name, get_rank_colour(int(level / 10) + 1), font=font)
    draw.text((96, 62), "LEVEL " + str(level), (255, 255, 255), font=font_big)
    # Fill data
    width = draw.textsize(str(attk), font=font)[0]
    draw.text((241 - width, 122), str(attk), (255, 255, 255), font=font)

    width = draw.textsize(str(strg), font=font)[0]
    draw.text((241 - width, 150), str(strg), (255, 255, 255), font=font)

    width = draw.textsize(str(shooting), font=font)[0]
    draw.text((241 - width, 178), str(shooting), (255, 255, 255), font=font)

    width = draw.textsize("$" + util.to_money(player.money,True) , font=font)[0]
    draw.text((241 - width, 204), "$" + util.to_money(player.money,True) , (255, 255, 255), font=font)
    
    width= draw.textsize(str(player.quests_won), font=font)[0]
    draw.text((241 - width, 253), str(player.quests_won), (255, 255, 255), font=font)
    
    width = draw.textsize(str(player.wagers_won), font=font)[0]
    draw.text((241 - width, 267), str(player.wagers_won), (255, 255, 255), font=font)
    
    wep = get_text_limit_len(draw,util.clear_markdown_escapes(player.weapon.name),font,95);
    width = draw.textsize(wep, font=font)[0]
    draw.text((241 - width, 232), wep, (255, 255, 255), font=font)
    # here
    if(avatar != None):
        img.paste(avatar, (9, 12));
    c = 0;
    l = 0;
    first_even = True;
    for x in range(len(player.awards) - 1, -1, -1):
         if (c % 2 == 0):
             img.paste(award_icons[player.awards[x]], (18, 121 + 35 * l));
         else:
             img.paste(award_icons[player.awards[x]], (53, 121 + 35 * l));
             l = l + 1;
         c = c + 1;
         if(c == 8):
             break;
    if(len(player.awards) > 8):
        draw.text((18, 267), "+ " + str(len(player.awards) - 8) + " More", (48, 48, 48), font=font);
    if(len(player.awards) == 0):
        draw.text((38, 183), "None", (48, 48, 48), font=font);
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await util.get_client(message.server.id).send_file(message.channel, fp=output, filename="myinfo.png",content=":pen_fountain: **"+player.name+"'s** information.");
    output.close()


   # os.remove(fname + '.png')
    
async def displayQuestImage(quest, message):
    global images_served;
    images_served = images_served +1;
    await get_client(message.server.id).send_typing(message.channel);
    try:
        avatar = resize_avatar(quest, message.server, True, 72, 72);
    except:
        avatar = None;
    level = math.trunc(quest.level);
    attk = round(quest.attack, 2);
    strg = round(quest.strg, 2);
    shooting = round(quest.shooting, 2)
    img = Image.open("screens/stats_page_quest.png");
    draw = ImageDraw.Draw(img)
    name = get_text_limit_len(draw,util.clear_markdown_escapes(quest.name),font,114);
    g_quest = get_game_quest_from_id(quest.qID);
    draw.text((88, 38), name, getRankColour(int(level / 10) + 1), font=font)
    draw.text((134, 58), " " + str(level), (255, 255, 255), font=font_big)
    # Fill data
    width = draw.textsize(str(attk), font=font)[0]
    draw.text((203 - width, 123), str(attk), (255, 255, 255), font=font)

    width= draw.textsize(str(strg), font=font)[0]
    draw.text((203 - width, 151), str(strg), (255, 255, 255), font=font)

    width = draw.textsize(str(shooting), font=font)[0]
    draw.text((203 - width, 178), str(shooting), (255, 255, 255), font=font)

    wep = get_text_limit_len(draw,util.clear_markdown_escapes(get_weapon_from_id(quest.wID).name),font,136);
    width = draw.textsize(str(wep), font=font)[0]
    draw.text((203 - width, 207), str(wep), (255, 255, 255), font=font)
    
    if(g_quest != None):
        creator = get_text_limit_len(draw,g_quest.created_by,font,119);
        home = get_text_limit_len(draw,g_quest.made_on,font,146);
    else:
        creator = "Unknown";
        home = "Unknown";
    
    width = draw.textsize(creator, font=font)[0]
    draw.text((203 - width, 228), creator, (255, 255, 255), font=font)
    
    width = draw.textsize(home, font=font)[0]
    draw.text((203 - width, 242), home, (255, 255, 255), font=font)
    
    width = draw.textsize("$" + util.to_money(quest.money,True), font=font_med)[0]
    draw.text((203 - width, 266), "$" + util.to_money(quest.money,True), (48, 48, 48), font=font_med)

    if(avatar != None):
        img.paste(avatar, (9, 12));
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="questinfo.png",content=":pen_fountain: Here you go.");
    output.close()
    
async def battle_image(message, pone, ptwo, btext):
    global images_served;
    images_served = images_served +1;
    sender = findPlayer(message.author.id);
    sender.last_image_request = time.time();
    await get_client(message.server.id).send_typing(message.channel);
    try:
        if(not isinstance(pone, activeQuest)):
            avatar_one = resize_avatar(pone, message.server, False, 54, 54);
        else:
            avatar_one = resize_avatar(pone, message.server, True, 54, 54);
    except:
        avatar_one = None;
    #print(not isinstance(ptwo, activeQuest));
    try:
        if(not isinstance(ptwo, activeQuest)):
            avatar_two = resize_avatar(ptwo, message.server, False, 54, 54);
        else:
            avatar_two = resize_avatar(ptwo, message.server, True, 54, 54);
    except:
        avatar_two = None;
    weapon_one = get_weapon_from_id(pone.wID);
    weapon_two = get_weapon_from_id(ptwo.wID);
    img = Image.open("screens/battle_screen.png");   
    width, height = img.size;
    if(avatar_one != None):
        img.paste(avatar_one, (9, 9));
    if(avatar_two != None):
        img.paste(avatar_two, (width - 9 - 55, 9));
        
    wep_image_one = resize_image_url(weapon_one.image_url, 30, 30);
    
    if(wep_image_one == None):
        wep_image_one = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30);
		
    try:
        img.paste(wep_image_one, (6, height - 6 - 30), wep_image_one);
    except:
        img.paste(wep_image_one, (6, height - 6 - 30));
        
    wep_image_two = resize_image_url(weapon_two.image_url, 30, 30);
    
    if(wep_image_two == None):
        wep_image_two = resize_image_url(Weapons[no_weapon_id].image_url, 30, 30);
    try:
        img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30), wep_image_two);
    except:
        img.paste(wep_image_two, (width - 30 - 6, height - 6 - 30));
        
    draw = ImageDraw.Draw(img)
    draw.text((7, 64), "LEVEL " + str(math.trunc(pone.level)), (255, 255, 255), font=font_small)
    draw.text((190, 64), "LEVEL " + str(math.trunc(ptwo.level)), (255, 255, 255), font=font_small)
    weap_one_name = get_text_limit_len(draw,util.clear_markdown_escapes(weapon_one.name),font,85)
    width = draw.textsize(weap_one_name, font=font)[0]
    draw.text((124 - width, 88), weap_one_name, (255, 255, 255), font=font)
    draw.text((132, 103), get_text_limit_len(draw,util.clear_markdown_escapes(weapon_two.name),font,85), (255, 255, 255), font=font)
    output = BytesIO()
    img.save(output,format="PNG")
    output.seek(0);
    await get_client(message.server.id).send_file(message.channel, fp=output, filename="battle.png");
    await get_client(message.server.id).send_message(message.channel,btext);
    output.close()
    

def get_text_limit_len(draw,text,given_font,length):
    removed_chars = False;
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    for x in range(0, len(text)):
        width = draw.textsize(text, font=given_font)[0];
        if(width > length):
            text = text[:len(text)-1];
            removed_chars = True;
        else:
            if removed_chars:
                if (given_font != font_epic):
                    return text[:-1] + u"\u2026"
                else:
                    return text[:-3] + "..."
            return text;
