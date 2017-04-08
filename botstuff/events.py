from botstuff import commands,util

class MessageEvent(list):
  
    async def __call__(self,ctx):
      for listener in self:
          if await listener(ctx):
              break

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)
        
    def append(self,function):
        old = (find_old(function,self))
        if old == -1:
            super(MessageEvent, self).append(function)
        else:
            self[old] = function
        
class CommandEvent(dict):
  
    """Command event subscription.
    
    """
    
    def command_list(self,*args):
         filter_func = (lambda command : command) if len(args) == 0 else args[0]
         return ', '.join([command.__name__ for command in filter(filter_func,self.values()) if not command.is_hidden])
    
    def __str__(self):
         return "Command(%s)" % self.command_list()
         
    def __repr__(self):
        return "Command(%s)" % dict.__repr__(self)
  
    async def __call__(self,ctx):
        if not ctx.content.startswith(util.get_server_cmd_key(ctx.server)):
            return
        args = commands.parse(ctx)
        command = args[1]
        if command in self:
            await self[command](ctx,*args)
                
message_event = MessageEvent()
command_event = CommandEvent()

async def on_message_event(ctx):
    await message_event(ctx)
    await command_event(ctx)
        
def find_old(function,listeners):
    return next((index for index,listener in enumerate(listeners) if listener.__name__ == function.__name__),-1)
    
def register_message_listener(function):
    message_event.append(function)
        
def remove_message_listener(function):
    message_event.remove(function)

def register_command(command_function):
    command_event[command_function.__name__] = command_function

def remove_command(command_function):
    del command_event[command_function.__name__]

def get_command(command_name):
    command_name = command_name.lower()
    if command_name in command_event:
        return command_event[command_name]
