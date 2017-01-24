import discord;

command_event = Event();

class Event(list):
  
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    """
    
    def __call__(self,ctx, *args, **kwargs):
        for f in self:
            f(ctx, *args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)
        
def on_command_event():
    print("do stuff");
        
def register_command(command_function):
    command_event.append(command_function);
    
def remove_command(command_function):
    command_event.remove(command_function);

