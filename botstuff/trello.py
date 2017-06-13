import aiohttp

"""
Some basic trello actions
"""
    
class TrelloClient():
  
    """
    A very basic trello client with just the stuff I need &
    nothing extra
    """
  
    base_request = 'https://trello.com/1/'
  
    def __init__(self,api_key,api_token):
        self.api_key = api_key
        self.api_token = api_token
        self.key_and_token = {'key':api_key,'token':api_token}

    async def get_boards(self):
        return await self.fetch_json('members/me/boards')

    async def get_lists(self,board_id):
        return await self.fetch_json('boards/%s/lists' % board_id)

    async def fetch_json(self,url):
        async with aiohttp.get(self.base_request+url,params=self.key_and_token) as response: 
            return await response.json()
            
    async def get_labels(self,board_id):
        return await self.fetch_json('boards/%s/labels' % board_id)
      
    async def add_card(self,**details):
      
        """
        The main thing I need. Adding cards.
        
        This just used the board URL and and the names of lists etc
        since that is easier to work with
        """
        
        board_url = details["board"]
        list_name = details["list"]
        labels = details.get('labels',None)
        name = details["name"]
        description = details["desc"]
        
        for board in await self.get_boards():
            if board["url"] == board_url:
                lists = await self.get_lists(board["id"])
                
                for trello_list in lists:
                    if trello_list["name"].lower() == list_name.lower():
                      
                        label_ids = ''
                        
                        if labels != None:
                            labels = list(map(str.lower, labels))
                            board_labels = await self.get_labels(board["id"])
                            
                            label_ids_list = [label["id"] for label in board_labels if label["name"].lower() in labels]
                            if len(label_ids_list) != len(labels):
                                raise "Could not find labels"
                            label_ids = ','.join(label_ids_list)
                        
                        args = {'name':name,
                                'desc':description,
                                'idList':trello_list["id"],
                                'idLabels':label_ids}
                        
                        card_url = "cards"
                        
                        async with aiohttp.post(self.base_request+card_url,params=self.key_and_token,data=args) as response: 
                            result = await response.json()
                            if "shortUrl" in result:
                                return result["shortUrl"]
                            raise "Failed to add card!"
                raise "List not found"
        raise "Board not found"
                              
