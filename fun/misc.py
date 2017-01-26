auto_replies = [];

class AutoReply:
  
    def __init__(self,server_id,message,key,**kwargs):
        self.message = message;
        self.key = key;
        self.target = kwargs.get('target_user',None);
        self.server_id = server_id;
        channel = kwargs.get('channel_id',"all");
