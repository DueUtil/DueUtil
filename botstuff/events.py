import discord;
import asyncio;
from botstuff import commands

class MessageEvent(list):
  
    async def __call__(self,ctx):
      for listener in self:
          if await listener(ctx):
              break;

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)
        
class CommandEvent(MessageEvent):
  
    """Command event subscription.
    
    """
  
    async def __call__(self,ctx):
        for command in self:
            if await command(ctx, *commands.parse(ctx)):
                break;
                
message_event = MessageEvent();
command_event = CommandEvent();
        
async def on_message_event(ctx):
    await message_event(ctx);
    await command_event(ctx);
        
def register_message_listener(function):
    message_event.append(function);
    
def remove_message_listener(function):
    message_event.remove(function);

def register_command(command_function):
    command_event.append(command_function);
    
def remove_command(command_function):
    command_event.remove(command_function);

