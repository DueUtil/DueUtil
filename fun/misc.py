from botstuff import util, dbconn

POSTIVE_BOOLS = ('true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh')
auto_replies = []

class AutoReply:
  
    def __init__(self,server_id,message,key,**kwargs):
        self.message = message
        self.key = key
        self.target = kwargs.get('target_user',None)
        self.server_id = server_id
        channel = kwargs.get('channel_id',"all")
        
class DueUtilObject():
    
    def __init__(self,id,*args):
        self.id = id
        if len(args) > 0:
            self.name = args[0]
        
    @property
    def clean_name(self):
        return util.ultra_escape_string(self.name)
        
    @property
    def assii_name(self):
        return util.filter_string(self.name)
        
    def save(self):
        dbconn.insert_object(self.id,self)
        
async def random_word(message):
    response = requests.get("http://randomword.setgetgo.com/get.php")
    await create_glitter_text(message, response.text)
        

async def create_glitter_text(channel,gif_text):
    response = requests.get("http://www.gigaglitters.com/procesing.php?text="+parse.quote_plus(gif_text)
    +"&size=90&text_color=img/DCdarkness.gif&angle=0&border=0&border_yes_no=4&shadows=1&font='fonts/Super 911.ttf'")
    html = response.text
    soup = BeautifulSoup(html,"html.parser")
    box = soup.find("textarea", {"id": "dLink"})
    gif_text_area = str(box)
    gif_url = gif_text_area.replace('<textarea class="field" cols="12" id="dLink" onclick="this.focus();this.select()" readonly="">',"",1).replace('</textarea>',"",1)
    gif = io.BytesIO(requests.get(gif_url).content)
    await client.send_file(message.channel,fp=gif,filename='glittertext.gif')
