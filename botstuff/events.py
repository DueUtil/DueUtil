import discord;
import asyncio;
from botstuff import commands,util;

class MessageEvent(list):
  
    async def __call__(self,ctx):
      for listener in self:
          if await listener(ctx):
              break;

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)
        
    def append(self,function):
        old = (find_old(function,self));
        if old == -1:
            super(MessageEvent, self).append(function);
        else:
            self[old] = function
        
class CommandEvent(MessageEvent):
  
    """Command event subscription.
    
    """
    
    def command_list(self,*args):
         filter_func = (lambda command : command) if len(args) == 0 else args[0];
         return ', '.join([command.__name__ for command in filter(filter_func,self) if not command.is_hidden]);
    
    def __str__(self):
         return self.command_list();
  
    async def __call__(self,ctx):
        if not ctx.content.startswith(util.get_server_cmd_key(ctx.server)):
            return;
        args = commands.parse(ctx);
        for command in self:
            if await command(ctx,*args):
                break;
                
message_event = MessageEvent();
command_event = CommandEvent();

async def on_message_event(ctx):
    await message_event(ctx);
    await command_event(ctx);
        
def find_old(function,listeners):
    return next((index for index,listener in enumerate(listeners) if listener.__name__ == function.__name__),-1)
    
def register_message_listener(function):
    message_event.append(function);
        
def remove_message_listener(function):
    message_event.remove(function);

def register_command(command_function):
    command_event.append(command_function);

    
def remove_command(command_function):
    command_event.remove(command_function);

def get_command(command_name):
    for command in command_event:
        if command.__name__ == command_name.lower():
            return command;
    return None;
