import discord;
import asyncio;
from commands.util import commands

class CommandEvent(list):
  
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

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
    
def remove_command(command_function):
    command_event.remove(command_function);

