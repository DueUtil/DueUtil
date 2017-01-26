import discord;
import asyncio;
from botstuff import commands

class CommandEvent(list):
  
    """Command event subscription.
    
    """
   
    async def __call__(self,ctx):
        for command in self:
            await command(ctx, *commands.parse(ctx))

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)
        
command_event = CommandEvent();
        
async def on_command_event(ctx):
    await command_event(ctx);
        
def register_command(command_function):
    command_event.append(command_function);
    print(command_event);
    
def remove_command(command_function):
    command_event.remove(command_function);

