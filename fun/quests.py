from fun import players;

def get_server_quest_list(server):
    number = 0;
    text = "";
    if(server.id in ServersQuests):
        for quest in ServersQuests[server.id].values():
            number = number + 1;
            text = text + str(number) + ". " + quest.quest + " [" + quest.monsterName + "] \n";  
    if(number == 0):
        text =  "There isn't any quests on this server!\n";
    return text;

async def show_quest_list(message):
    title = message.server.name + " Quests**\n**Square brackets indicate quest name.";
    title_not_first_page = message.server.name + " Quests";
    last_page_footer ="That's it!"
    await util.display_with_pages(message,get_server_quest_list(message.server),"serverquests",title,title_not_first_page,"",last_page_footer);
                        
async def manage_quests(message):
    global quests_given;
    player = findPlayer(message.author.id);  
    if(time.time() - player.quest_day_start > 86400 and player.quest_day_start != 0):
        player.quests_completed_today = 0;
        player.quest_day_start = 0;
        print(filter_func(player.name)+" ("+player.userid+") daily completed quests reset");
    if(message.server.id not in ServersQuests and not os.path.isfile("saves/gamequests/"+message.server.id)):
        addQuests(message.server.id);
    if((time.time() - player.last_quest) >= 360):
        player.last_quest = time.time();
        if(message.server.id in ServersQuests and len(ServersQuests[message.server.id]) >= 1):
            n_q = ServersQuests[message.server.id][random.choice(list(ServersQuests[message.server.id].keys()))];
            if (random.random()<(n_q.spawnchance*(5/((player.quests_completed_today+5)*30))) and len(player.quests) <= 6):
                await addQuest(message, player, n_q);
                quests_given += 1;
                print(filter_func(player.name)+" ("+player.userid+") has received a quest ["+filter_func(n_q.qID)+"]");

async def add_quest(message, player, n_q):
    aQ = createQuest(n_q, player);
    savePlayer(player);
    if(not(message.server.id+"/"+message.channel.id in util.mutedchan)):
        await new_quest_image(message, aQ, player);
    else:
        print("Won't send new quest image - channel blocked.")

def create_quest(n_q, player):
    aQ = activeQuest();
    aQ.qID = n_q.qID;
    aQ.level = random.randint(int(player.level), int((player.level * 2)))
    hpMtp = random.randint(int(aQ.level / 2), int(aQ.level));
    shootMtp = random.randint(int(aQ.level / 2), int(aQ.level)) / random.uniform(1.5, 1.9);
    strgMtp = random.randint(int(aQ.level / 2), int(aQ.level)) / random.uniform(1.5, 1.9);
    attackMtp = random.randint(int(aQ.level / 2), int(aQ.level)) / random.uniform(1.5, 1.9);
    aQ.name = n_q.monsterName;
    aQ.hp = n_q.basehp * hpMtp;
    aQ.attack = n_q.baseattack * attackMtp;
    aQ.strg = n_q.basestrg * strgMtp;
    aQ.shooting = n_q.baseshooting * shootMtp;
    aQ.money = abs(int(n_q.bwinings) * int((hpMtp + shootMtp + strgMtp + attackMtp) / 4));
    if (aQ.money == 0):
        aQ.money = 1;
    aQ.wID =n_q.wID;
    player.quests.append(aQ);
    return aQ;

async def show_quests(message):
      player = findPlayer(message.author.id);
      command_key = util.get_server_cmd_key(message.server);
      QuestsT = "```\n" + player.name + "'s Quests!\n"
      if len(player.quests) > 0:
          for x in range(0, len(player.quests)):
              try:
                  real_quest = get_game_quest_from_id(player.quests[x].qID);
                  if(real_quest != None):
                      questT = real_quest.quest;
                  else:
                      questT = "Long forgotten quest:";
              except:
                  questT = "Long forgotten quest:";
              QuestsT = QuestsT + str(x + 1) + ". " + questT + " " + player.quests[x].name + " [Level " + str(player.quests[x].level) + "]!\n";
          QuestsT = QuestsT + "Use " + command_key + "declinequest [Quest Number] to remove a quest.\n";
          QuestsT = QuestsT + "Use " + command_key + "acceptquest [Quest Number] to accept!\n";
          QuestsT = QuestsT + "Use " + command_key + "questinfo [Quest Number] for more information!\n```";
      else:
          QuestsT = QuestsT + "You don't have any quests!```";
      await get_client(message.server.id).send_message(message.channel, QuestsT);
      
def load_quests():
    global ServersQuests;
    for file in os.listdir("saves/gamequests/"):
        if file.endswith(".json"):
            with open("saves/gamequests/" + str(file)) as data_file:    
                try:
                    data = json.load(data_file);
                    q = jsonpickle.decode(data);
                    if(q.baseattack < 1 or q.basestrg < 1 or q.basehp < 30 or q.baseshooting < 1):
                        os.remove("saves/gamequests/" + str(file));
                        print("Quest removed! - Invalid stats!");
                        continue;
                    if(q.update):
                        q.spawnchance = update_chance(False,q.spawnchance);
                        q.update = False;
                        saveQuest(q);
                    args = util.get_strings(q.qID);
                    if(len(args) == 2):
                        if(args[0] in ServersQuests):
                            ServersQuests[args[0]][args[1]] = q;
                        else:
                            ServersQuests[args[0]]=dict();
                            ServersQuests[args[0]][args[1]] = q;
                    else:
                        print("Failed to load quest!")
                except:
                    print("Quest data corrupt!");  

    
def add_quest(quest):
    global server_quests;
    
    server_quests[quest.server_id][quest.monster_name.lower()] = quest;
    save_quest(quest);
    
